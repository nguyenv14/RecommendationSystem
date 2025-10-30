try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence_transformers OK")
    print("Version:", SentenceTransformer.__module__)
except Exception as e:
    print("✗ Error:", e)
    import traceback
    traceback.print_exc()


