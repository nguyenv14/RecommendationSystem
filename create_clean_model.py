#!/usr/bin/env python3
"""
Script để tạo model NCF sạch hơn từ dữ liệu đã được làm sạch
"""

import pandas as pd
import numpy as np
import json
import tensorflow as tf
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Thiết lập TensorFlow
tf.config.run_functions_eagerly(True)
tf.data.experimental.enable_debug_mode()

def load_data():
    """Load dữ liệu đã được xử lý"""
    print("📂 Đang load dữ liệu...")
    
    # Load interactions
    interactions_df = pd.read_parquet("interactions_parquet.snappy")
    print(f"   📊 Interactions: {len(interactions_df)} dòng")
    
    # Load mappings
    with open("user2idx.json", "r") as f:
        user2idx = json.load(f)
    with open("hotel2idx.json", "r") as f:
        hotel2idx = json.load(f)
    
    print(f"   👥 Users: {len(user2idx)}")
    print(f"   🏨 Hotels: {len(hotel2idx)}")
    
    return interactions_df, user2idx, hotel2idx

def clean_data(interactions_df, user2idx, hotel2idx):
    """Làm sạch dữ liệu để tránh data leakage"""
    print("🧹 Đang làm sạch dữ liệu...")
    
    # Đếm số interactions per user
    user_counts = interactions_df.groupby('user_idx').size()
    print(f"   📊 Số interactions per user:")
    print(f"      Min: {user_counts.min()}")
    print(f"      Max: {user_counts.max()}")
    print(f"      Mean: {user_counts.mean():.2f}")
    
    # Loại bỏ users có quá nhiều interactions (có thể là data leakage)
    suspicious_users = user_counts[user_counts > 15].index
    print(f"   ⚠️ Users có >15 interactions: {len(suspicious_users)}")
    
    if len(suspicious_users) > 0:
        print(f"   🗑️ Loại bỏ {len(suspicious_users)} users nghi ngờ...")
        clean_interactions = interactions_df[~interactions_df['user_idx'].isin(suspicious_users)]
        print(f"   📊 Sau khi làm sạch: {len(clean_interactions)} interactions")
    else:
        clean_interactions = interactions_df.copy()
    
    # Tạo mapping mới cho clean data
    clean_users = sorted(clean_interactions['user_idx'].unique())
    clean_hotels = sorted(clean_interactions['hotel_idx'].unique())
    
    clean_user2idx = {str(user): idx for idx, user in enumerate(clean_users)}
    clean_hotel2idx = {str(hotel): idx for idx, hotel in enumerate(clean_hotels)}
    
    print(f"   ✅ Clean users: {len(clean_user2idx)}")
    print(f"   ✅ Clean hotels: {len(clean_hotel2idx)}")
    
    return clean_interactions, clean_user2idx, clean_hotel2idx

def create_balanced_dataset(interactions_df, num_hotels, neg_ratio=1.0, seed=42):
    """Tạo dataset cân bằng với negative sampling"""
    print("⚖️ Tạo dataset cân bằng...")
    
    # Lấy positive interactions
    pos_interactions = interactions_df[interactions_df['label'] == 1].copy()
    print(f"   📊 Positive interactions: {len(pos_interactions)}")
    
    # Negative sampling
    rng = np.random.RandomState(seed)
    user_pos = pos_interactions.groupby('user_idx')['hotel_idx'].apply(set).to_dict()
    
    neg_rows = []
    all_hotels = np.arange(num_hotels)
    
    for user_idx, pos_set in user_pos.items():
        n_pos = len(pos_set)
        n_neg = int(n_pos * neg_ratio)
        
        sampled = set()
        attempts = 0
        max_attempts = n_neg * 10
        
        while len(sampled) < n_neg and attempts < max_attempts:
            cand = rng.randint(0, num_hotels)
            if cand not in pos_set:
                sampled.add(cand)
            attempts += 1
        
        for hotel_idx in sampled:
            neg_rows.append({
                'user_idx': user_idx,
                'hotel_idx': hotel_idx,
                'label': 0
            })
    
    neg_df = pd.DataFrame(neg_rows)
    print(f"   📊 Negative interactions: {len(neg_df)}")
    
    # Combine và shuffle
    combined = pd.concat([pos_interactions, neg_df], ignore_index=True)
    combined = combined.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    print(f"   ✅ Total dataset: {len(combined)}")
    print(f"   📊 Positive ratio: {(combined['label'] == 1).mean():.3f}")
    
    return combined

def df_to_tf_dataset(df, shuffle=True, batch_size=2048):
    """Convert DataFrame to TensorFlow Dataset"""
    inputs = {
        "user_idx": df["user_idx"].values.astype("int32"),
        "hotel_idx": df["hotel_idx"].values.astype("int32")
    }
    targets = df["label"].values.astype("float32")
    
    ds = tf.data.Dataset.from_tensor_slices((inputs, targets))
    
    if shuffle:
        ds = ds.shuffle(buffer_size=len(df))
    
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds

def build_ncf_model(num_users, num_items, embedding_dim=64):
    """Xây dựng NCF model"""
    print("🏗️ Xây dựng NCF model...")
    
    # Input layers
    user_input = tf.keras.layers.Input(shape=(), name="user_idx", dtype=tf.int32)
    item_input = tf.keras.layers.Input(shape=(), name="hotel_idx", dtype=tf.int32)
    
    # Embedding layers
    user_embedding = tf.keras.layers.Embedding(
        input_dim=num_users,
        output_dim=embedding_dim,
        name="user_embedding"
    )(user_input)
    
    item_embedding = tf.keras.layers.Embedding(
        input_dim=num_items,
        output_dim=embedding_dim,
        name="item_embedding"
    )(item_input)
    
    # Flatten embeddings
    user_vec = tf.keras.layers.Flatten()(user_embedding)
    item_vec = tf.keras.layers.Flatten()(item_embedding)
    
    # Concatenate
    concat = tf.keras.layers.Concatenate()([user_vec, item_vec])
    
    # MLP layers
    mlp = tf.keras.layers.Dense(128, activation="relu")(concat)
    mlp = tf.keras.layers.Dropout(0.2)(mlp)
    mlp = tf.keras.layers.Dense(64, activation="relu")(mlp)
    mlp = tf.keras.layers.Dropout(0.2)(mlp)
    mlp = tf.keras.layers.Dense(32, activation="relu")(mlp)
    
    # Output
    output = tf.keras.layers.Dense(1, activation="sigmoid")(mlp)
    
    model = tf.keras.Model(inputs=[user_input, item_input], outputs=output)
    
    return model

def train_model(model, train_ds, val_ds, epochs=50):
    """Train model"""
    print("🚀 Bắt đầu training...")
    
    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
    )
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_auc",
            patience=10,
            restore_best_weights=True,
            mode="max"
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
    ]
    
    # Train
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def save_model_and_data(model, clean_user2idx, clean_hotel2idx, clean_dataset, model_dir):
    """Lưu model và dữ liệu"""
    print("💾 Đang lưu model và dữ liệu...")
    
    model_dir = Path(model_dir)
    model_dir.mkdir(exist_ok=True)
    
    # Save model
    model.save(model_dir / "saved_model")
    model.save_weights(model_dir / "best_model.h5")
    
    # Save mappings
    with open(model_dir / "user2idx.json", "w") as f:
        json.dump(clean_user2idx, f, indent=2)
    
    with open(model_dir / "hotel2idx.json", "w") as f:
        json.dump(clean_hotel2idx, f, indent=2)
    
    # Save clean dataset
    clean_dataset.to_parquet(model_dir / "clean_interactions.parquet", compression="snappy")
    
    # Save embeddings
    user_embeddings = model.get_layer("user_embedding").get_weights()[0]
    item_embeddings = model.get_layer("item_embedding").get_weights()[0]
    
    np.save(model_dir / "user_embeddings.npy", user_embeddings)
    np.save(model_dir / "item_embeddings.npy", item_embeddings)
    
    print(f"   ✅ Đã lưu vào: {model_dir}")

def main():
    """Main function"""
    print("🎯 Tạo Clean NCF Model")
    print("=" * 50)
    
    # Load data
    interactions_df, user2idx, hotel2idx = load_data()
    
    # Clean data
    clean_interactions, clean_user2idx, clean_hotel2idx = clean_data(
        interactions_df, user2idx, hotel2idx
    )
    
    # Map lại indices cho clean data
    clean_dataset = clean_interactions.copy()
    clean_dataset['user_idx'] = clean_dataset['user_idx'].map({int(k): v for k, v in clean_user2idx.items()})
    clean_dataset['hotel_idx'] = clean_dataset['hotel_idx'].map({int(k): v for k, v in clean_hotel2idx.items()})
    
    # Loại bỏ NaN values
    clean_dataset = clean_dataset.dropna(subset=['user_idx', 'hotel_idx'])
    clean_dataset['user_idx'] = clean_dataset['user_idx'].astype(int)
    clean_dataset['hotel_idx'] = clean_dataset['hotel_idx'].astype(int)
    
    print(f"📊 Clean dataset: {len(clean_dataset)} interactions")
    
    # Create balanced dataset
    balanced_dataset = create_balanced_dataset(
        clean_dataset, 
        len(clean_hotel2idx), 
        neg_ratio=1.0
    )
    
    # Split data
    train_df, val_df = train_test_split(
        balanced_dataset, 
        test_size=0.2, 
        random_state=42,
        stratify=balanced_dataset['label']
    )
    
    print(f"📊 Train: {len(train_df)}, Val: {len(val_df)}")
    
    # Convert to TensorFlow datasets
    train_ds = df_to_tf_dataset(train_df)
    val_ds = df_to_tf_dataset(val_df, shuffle=False)
    
    # Build model
    model = build_ncf_model(
        num_users=len(clean_user2idx),
        num_items=len(clean_hotel2idx),
        embedding_dim=64
    )
    
    print(f"📊 Model parameters: {model.count_params():,}")
    
    # Train model
    history = train_model(model, train_ds, val_ds, epochs=50)
    
    # Save everything
    save_model_and_data(
        model, 
        clean_user2idx, 
        clean_hotel2idx, 
        balanced_dataset,
        "models/clean_ncf"
    )
    
    print("\n🎉 Hoàn thành!")
    print(f"📁 Model đã được lưu tại: models/clean_ncf")

if __name__ == "__main__":
    main()
