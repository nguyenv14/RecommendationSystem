-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 11, 2025 at 05:34 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `myhotel`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_roles`
--

CREATE TABLE `admin_roles` (
  `admin_roles_id` int(11) NOT NULL,
  `admin_admin_id` int(11) UNSIGNED NOT NULL,
  `roles_roles_id` int(11) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin_roles`
--

INSERT INTO `admin_roles` (`admin_roles_id`, `admin_admin_id`, `roles_roles_id`) VALUES
(1, 1, 1),
(8, 2, 2),
(12, 3, 3),
(13, 5, 4);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_activitylog`
--

CREATE TABLE `tbl_activitylog` (
  `activitylog_id` int(10) UNSIGNED NOT NULL,
  `activitylog_admin_id` int(10) UNSIGNED DEFAULT NULL,
  `activitylog_customer_id` int(10) UNSIGNED DEFAULT NULL,
  `activitylog_admin_name` varchar(256) DEFAULT NULL,
  `activitylog_customer_name` varchar(256) DEFAULT NULL,
  `activitylog_type` int(10) UNSIGNED NOT NULL,
  `activitylog_proceed` varchar(256) NOT NULL,
  `activitylog_ip` varchar(256) NOT NULL,
  `activitylog_located` varchar(256) NOT NULL,
  `activitylog_device` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `tbl_admin`
--

CREATE TABLE `tbl_admin` (
  `admin_id` int(10) UNSIGNED NOT NULL,
  `admin_email` varchar(100) NOT NULL,
  `admin_password` varchar(32) NOT NULL,
  `admin_name` varchar(32) NOT NULL,
  `admin_phone` varchar(10) NOT NULL,
  `hotel_id` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_admin`
--

INSERT INTO `tbl_admin` (`admin_id`, `admin_email`, `admin_password`, `admin_name`, `admin_phone`, `hotel_id`, `created_at`, `updated_at`) VALUES
(1, 'admin@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', 'Quản Trị Viên', '0987654321', NULL, '2022-10-23 06:50:51', '2022-10-23 06:50:51'),
(2, 'nhanmanager@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', 'Nhân Quản Lý', '0987654321', NULL, '2022-10-23 07:47:33', '2022-10-23 07:47:33'),
(3, 'nhanemployee@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', 'Nhân Nhân Viên', '0987654321', NULL, '2022-10-23 07:47:56', '2022-10-23 07:47:56'),
(5, 'nguyen@haiau.com', 'e10adc3949ba59abbe56e057f20f883e', 'Nguyễn Văn Vĩnh Nguyên', '0839519415', 22, '2025-10-06 14:34:34', '2025-10-06 14:34:34');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_area`
--

CREATE TABLE `tbl_area` (
  `area_id` int(11) NOT NULL,
  `area_name` varchar(256) NOT NULL,
  `area_desc` varchar(256) NOT NULL,
  `area_image` varchar(256) NOT NULL,
  `area_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_area`
--

INSERT INTO `tbl_area` (`area_id`, `area_name`, `area_desc`, `area_image`, `area_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(3, 'Cẩm Lệ', 'Cẩm Lệ', 'camle47.png', 1, '2022-10-29 18:45:14', NULL, NULL),
(4, 'Hải Châu', 'Hải Châu', 'haichau40.png', 1, '2022-10-29 18:45:44', NULL, NULL),
(5, 'Hòa Vang', 'Hòa Vang', 'hoavang63.png', 1, '2022-10-29 18:46:01', NULL, NULL),
(6, 'Liên Chiểu', 'Liên Chiểu', 'lienchieu66.png', 1, '2022-10-29 18:46:19', NULL, NULL),
(7, 'Ngũ Hành Sơn', 'Ngũ Hành Sơn', 'Nguhanhson90.png', 1, '2022-10-29 18:46:35', NULL, NULL),
(8, 'Sơn Trà', 'Sơn Trà', 'sontra1.png', 1, '2022-10-29 18:46:48', NULL, NULL),
(9, 'Thanh Khê', 'Thanh Khê', 'thanhke42.png', 1, '2022-10-29 18:47:04', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_bannerads`
--

CREATE TABLE `tbl_bannerads` (
  `bannerads_id` int(11) NOT NULL,
  `bannerads_title` varchar(256) NOT NULL,
  `bannerads_desc` varchar(256) NOT NULL,
  `bannerads_page` int(1) NOT NULL,
  `bannerads_link` varchar(255) NOT NULL,
  `bannerads_image` varchar(256) NOT NULL,
  `bannerads_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_bannerads`
--

INSERT INTO `tbl_bannerads` (`bannerads_id`, `bannerads_title`, `bannerads_desc`, `bannerads_page`, `bannerads_link`, `bannerads_image`, `bannerads_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(4, 'Đà Nẵng Thân Yêu, Thân Thiện <3', 'Đà Nẵng Thân Yêu <3', 2, 'https://nhuandeptraivanhanbro.doancoso2.laravel.vn/DoAnCoSo2/khach-san-chi-tiet?hotel_id=3', 'app-push-104567.png', 1, '2022-12-22 14:40:14', '2024-04-24 09:36:57', NULL),
(5, 'ĐẾN MÙA RỒI ! LÊN SAPA SĂN MÂY THÔI', 'Nhân Test Banner ADS', 2, 'https://nhuandeptraivanhanbro.doancoso2.laravel.vn/DoAnCoSo2/', 'app-push60.png', 1, '2022-12-22 14:48:37', NULL, NULL),
(6, 'CHRISTMAS SALE Deal ngon đừng bỏ lỡ', 'Giáng Sinh An Lành', 1, 'https://nhuandeptraivanhanbro.doancoso2.laravel.vn/DoAnCoSo2/', '1180x50063.jpg', 0, '2022-12-24 14:10:18', '2023-08-18 14:07:59', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_brand`
--

CREATE TABLE `tbl_brand` (
  `brand_id` int(10) UNSIGNED NOT NULL,
  `brand_name` varchar(255) NOT NULL,
  `brand_desc` varchar(255) NOT NULL,
  `brand_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_brand`
--

INSERT INTO `tbl_brand` (`brand_id`, `brand_name`, `brand_desc`, `brand_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 'Mường Thanh Hotel', 'Mường Thanh Hotel Group Ok', 1, '2022-10-29 14:34:43', '2022-10-31 16:18:33', NULL),
(2, 'Accor', 'Accor', 1, '2022-10-30 17:39:55', NULL, NULL),
(3, 'Furama', 'Furama', 1, '2022-10-30 17:40:06', NULL, NULL),
(4, 'InterContinental Hotels Group', 'InterContinental Hotels Group', 1, '2022-10-30 17:40:15', NULL, NULL),
(5, 'Meliá Hotels International', 'Meliá Hotels International', 1, '2022-10-30 17:40:23', NULL, NULL),
(6, 'Pullman', 'Pullman', 1, '2022-10-30 17:40:36', '2022-10-30 17:41:18', NULL),
(7, 'Sheraton', 'Sheraton', 1, '2022-10-30 17:40:43', NULL, NULL),
(8, 'Vinpearl', 'Vinpearl', 1, '2022-10-30 17:40:50', '2022-10-30 17:41:16', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_company_config`
--

CREATE TABLE `tbl_company_config` (
  `company_id` int(20) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `company_hostline` varchar(1000) DEFAULT NULL,
  `company_mail` varchar(1000) DEFAULT NULL,
  `company_address` text DEFAULT NULL,
  `company_slogan` text DEFAULT NULL,
  `company_copyright` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_company_config`
--

INSERT INTO `tbl_company_config` (`company_id`, `company_name`, `company_hostline`, `company_mail`, `company_address`, `company_slogan`, `company_copyright`) VALUES
(11, 'Công ty cổ phần du lịch Việt Nam MyHotel', '1900 1900', 'nhanlk@vku.udn.vn', 'KTX Khu 2, Phòng 210 , Trường Việt Hàn', 'MyHotel là thành viên của VNTravel Group - Một trong những tập đoàn đứng đầu Đông Nam Á về du lịch trực tuyến và các dịch vụ liên quan.', 'Copyright © 2022 - ĐỒ ÁN CƠ SỞ 2 WEBSITE HỖ TRỢ TÌM KIẾM KHÁCH SẠN - NHUẬN BÁO THỦ - LÊ KHẢ NHÂN - WEBSITE ĐƯỢC THIẾT KẾ VÀO 23/10/2022');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_configweb`
--

CREATE TABLE `tbl_configweb` (
  `config_id` int(111) NOT NULL,
  `config_image` varchar(255) NOT NULL,
  `config_title` varchar(255) NOT NULL,
  `config_content` varchar(255) NOT NULL,
  `config_type` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_configweb`
--

INSERT INTO `tbl_configweb` (`config_id`, `config_image`, `config_title`, `config_content`, `config_type`, `created_at`, `updated_at`) VALUES
(22, 'icon_best_price90.svg', 'Giá tốt sát ngày', 'Cam kết giá tốt nhất khi đặt gần ngày cho chuyến đi của bạn.', 2, '2022-10-23 15:11:46', '2022-10-23 15:15:22'),
(23, 'icon_payment7.svg', 'Thanh toán dễ dàng, đa dạng', 'Bao gồm thêm chuyển khoản ngân hàng và tiền mặt tại cửa hàng', 2, '2022-10-23 15:11:46', '2022-10-23 15:15:58'),
(24, 'icon_support_24797.svg', 'Hỗ trợ khách hàng 24/7', 'Chat là có, gọi là nghe, không quản đêm hôm, ngày nghỉ và ngày lễ.', 2, '2022-10-23 15:11:46', '2022-10-23 15:15:41'),
(25, 'icon_total_hotel32.svg', 'Hơn 8000+ khách sạn dọc Việt Nam', 'Hàng nghìn khách sạn, đặc biệt là 4 sao và 5 sao, cho phép bạn thoải mái lựa chọn, giá cạnh tranh, phong phú.', 2, '2022-10-23 15:11:46', '2022-10-23 15:19:16'),
(28, 'logo57.png', 'Ảnh này chưa có tiêu đề', 'Ảnh này chưa có nội dung !', 1, '2022-10-23 15:40:37', NULL),
(29, 'icon_company_group47.svg', 'Ảnh này chưa có tiêu đề', 'Ảnh này chưa có nội dung !', 3, '2022-10-23 15:41:47', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_coupon`
--

CREATE TABLE `tbl_coupon` (
  `coupon_id` int(10) UNSIGNED NOT NULL,
  `coupon_name` varchar(255) NOT NULL,
  `coupon_name_code` varchar(255) NOT NULL,
  `coupon_desc` varchar(256) NOT NULL,
  `coupon_qty_code` int(11) NOT NULL,
  `coupon_condition` int(11) NOT NULL,
  `coupon_price_sale` float NOT NULL,
  `coupon_start_date` varchar(256) DEFAULT NULL,
  `coupon_end_date` varchar(256) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_coupon`
--

INSERT INTO `tbl_coupon` (`coupon_id`, `coupon_name`, `coupon_name_code`, `coupon_desc`, `coupon_qty_code`, `coupon_condition`, `coupon_price_sale`, `coupon_start_date`, `coupon_end_date`, `created_at`, `updated_at`) VALUES
(5, 'Chào Đà Nẵng', 'CHAODANANG', 'Voucher ưu đãi khu vực Đà Nẵng', 9991, 1, 9, '2022-11-09', '2024-12-31', '2022-11-16 07:01:41', '2022-11-16 07:01:41'),
(6, 'Hello VKU', 'HELLOVKU', 'Voucher ưu đãi cho sinh viên VKU', 994, 1, 19, '2022-11-02', '2024-12-31', '2022-11-16 07:02:25', '2022-11-16 07:02:25'),
(7, 'Sếp Nguyên Mãi Đỉnh', 'SEPNGUYEN', 'Sếp Nguyên Báo Thủ Cân Team', 996, 1, 14, '2022-10-12', '2024-01-31', '2022-11-16 07:03:25', '2022-11-16 07:03:25'),
(8, 'Mã Hết Hạn', 'HETHAN', 'Mã Hết Hạn', 1000, 1, 99, '2022-09-10', '2022-11-30', '2022-11-16 07:04:12', '2022-11-16 07:04:12');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_customers`
--

CREATE TABLE `tbl_customers` (
  `customer_id` int(10) UNSIGNED NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `customer_phone` int(11) DEFAULT NULL,
  `customer_email` varchar(255) NOT NULL,
  `customer_password` varchar(255) DEFAULT NULL,
  `customer_status` int(11) NOT NULL,
  `customer_ip` varchar(256) DEFAULT NULL,
  `customer_located` varchar(256) DEFAULT NULL,
  `customer_device` varchar(256) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_customers`
--

INSERT INTO `tbl_customers` (`customer_id`, `customer_name`, `customer_phone`, `customer_email`, `customer_password`, `customer_status`, `customer_ip`, `customer_located`, `customer_device`, `created_at`, `updated_at`, `deleted_at`) VALUES
(3, 'Nhân Kha Le', 987654321, 'nhanlk.21it@vku.udn.vn', '202cb962ac59075b964b07152d234b70', 1, '127.0.0.1', 'Không Xác Định', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', '2022-10-25 10:59:34', '2024-05-15 07:50:24', NULL),
(5, 'Nhân', 987654321, 'nhan@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:17:19', '2022-10-27 03:28:32', NULL),
(6, 'Sếp Nhuận', 987654321, 'nhuan@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:17:56', '2022-10-25 13:24:14', '2022-10-25 06:24:14'),
(8, 'Sếp Nhuận Đz', 987654321, 'nhuan123321@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:18:19', '2022-10-25 12:28:21', NULL),
(9, ' Nhuận Đz', 987654321, 'nhuandz123321@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:18:32', '2022-10-25 12:49:20', NULL),
(10, ' Nhuận Báo', 987654321, 'nhuandz1221@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:18:41', '2022-10-25 12:27:57', NULL),
(11, ' Nhuận Báo Thủ', 987654321, 'nhuantrumcode@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:18:57', '2022-10-27 03:25:06', NULL),
(12, ' Nhuận Báo Thủ', 987654321, 'nhuanganhteam@vku.udn.vn\r\n', 'e10adc3949ba59abbe56e057f20f883e\r\n', 1, '127.0.0.1', 'QB', 'Win', '2022-10-25 12:19:12', '2022-10-25 13:26:28', '2022-10-25 06:26:28'),
(13, 'Nhân Lê Khả', NULL, 'nhanlekha@gmail.com', NULL, 1, '127.0.0.1', 'Không Xác Định', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', '2022-12-23 07:53:13', '2022-12-23 07:53:13', NULL),
(14, 'Nhuận Báo Thủ Cute', 987654321, 'phunhuanhuynh2003@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', 1, '127.0.0.1', 'Không Xác Định', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', '2022-12-24 13:12:19', '2022-12-24 13:12:19', NULL),
(15, 'Nguyễn Văn Vĩnh Nguyen', 839519415, 'nguyenvy1470@gmail.com', 'e10adc3949ba59abbe56e057f20f883e', 1, '::1', 'Không Xác Định', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0', '2024-05-05 12:37:09', '2025-10-04 10:22:42', NULL),
(16, 'Vanminh Tran', NULL, 'vanminh22199@gmail.com', NULL, 0, NULL, NULL, NULL, '2024-05-19 10:03:35', '2024-05-19 10:03:35', NULL),
(17, 'Nguyên Vĩnh', 839519415, 'nguyennvv.21it@vku.udn.vn', NULL, 0, NULL, NULL, NULL, '2024-06-01 17:18:13', '2024-06-01 17:19:11', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_evaluate`
--

CREATE TABLE `tbl_evaluate` (
  `evaluate_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `customer_name` varchar(256) NOT NULL,
  `hotel_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `type_room_id` int(11) NOT NULL,
  `evaluate_title` varchar(256) NOT NULL,
  `evaluate_content` varchar(10000) NOT NULL,
  `evaluate_loaction_point` int(11) NOT NULL,
  `evaluate_service_point` int(11) NOT NULL,
  `evaluate_price_point` int(11) NOT NULL,
  `evaluate_sanitary_point` int(11) NOT NULL,
  `evaluate_convenient_point` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_evaluate`
--

INSERT INTO `tbl_evaluate` (`evaluate_id`, `customer_id`, `customer_name`, `hotel_id`, `room_id`, `type_room_id`, `evaluate_title`, `evaluate_content`, `evaluate_loaction_point`, `evaluate_service_point`, `evaluate_price_point`, `evaluate_sanitary_point`, `evaluate_convenient_point`, `created_at`, `updated_at`, `deleted_at`) VALUES
(3, 13, 'Nhân Lê Khả', 6, 15, 43, 'Khách Sạn Tốt Lắm', 'Khách Sạn Tốt Lắm', 5, 5, 5, 5, 5, '2022-12-24 08:42:52', NULL, NULL),
(5, 13, 'Nhân Lê Khả', 3, 5, 3, 'Khách Sạn Tốt', 'Khách Sạn Tốt', 5, 5, 5, 5, 5, '2022-12-24 20:32:54', NULL, NULL),
(6, 3, 'Nhân', 3, 5, 3, 'Khách Sạn Ok', 'Tuyệt Vời', 5, 5, 5, 5, 5, '2023-08-18 07:02:07', NULL, NULL),
(8, 13, 'Nhân Lê Khả', 6, 15, 43, 'Khách Sạn Tốt Lắm', 'Khách Sạn Tốt Lắm', 5, 5, 5, 5, 5, '2022-12-24 08:42:52', NULL, NULL),
(9, 13, 'Nhân Lê Khả', 3, 5, 3, 'Khách Sạn Tốt', 'Khách Sạn Tốt', 5, 5, 5, 5, 5, '2022-12-24 20:32:54', NULL, NULL),
(10, 5, 'Nhân', 5, 3, 8, 'Khách Sạn Tuyệt Vời', 'Dịch vụ rất tốt, phòng ốc sạch sẽ, nhân viên thân thiện.', 5, 5, 4, 4, 5, '2022-12-24 21:15:32', NULL, NULL),
(12, 9, ' Nhuận Đz', 1, 8, 8, 'Nơi Nghỉ Dưỡng Tuyệt Vời', 'Phòng đẹp, không gian thoải mái, view đẹp.', 4, 5, 4, 4, 5, '2022-12-25 00:45:29', NULL, NULL),
(13, 10, ' Nhuận Báo', 4, 6, 8, 'Phòng Khách Sạn Rộng Rãi', 'Khách sạn có phòng rộng, sạch sẽ, đồ ăn ngon.', 4, 4, 4, 4, 4, '2022-12-25 02:20:54', NULL, NULL),
(14, 11, ' Nhuận Báo Thủ', 3, 7, 3, 'Dịch Vụ Tốt', 'Dịch vụ khách sạn rất tốt, nhân viên thân thiện.', 5, 5, 5, 5, 5, '2022-12-25 04:00:10', NULL, NULL),
(15, 12, ' Nhuận Báo Thủ', 2, 8, 8, 'Nghỉ Dưỡng Tuyệt Vời', 'Khách sạn đẹp, phòng ốc sạch sẽ, view đẹp.', 5, 5, 4, 4, 5, '2022-12-25 18:10:22', NULL, NULL),
(16, 13, 'Nhân Lê Khả', 2, 6, 3, 'Phòng Khách Sạn Rộng Rãi', 'Phòng khách sạn rộng rãi, thoải mái, nhân viên thân thiện.', 4, 4, 4, 4, 5, '2022-12-25 20:25:43', NULL, NULL),
(17, 14, 'Nhuận Báo Thủ Cute', 1, 4, 8, 'Nơi Nghỉ Dưỡng Lý Tưởng', 'Khách sạn có không gian đẹp, phòng ngủ thoải mái.', 5, 4, 4, 4, 4, '2022-12-25 22:40:55', NULL, NULL),
(18, 15, 'Nhân Lê Khả', 5, 2, 5, 'Dịch Vụ Tốt', 'Dịch vụ khách sạn tuyệt vời, phòng ốc sạch sẽ, không gian thoải mái.', 5, 5, 5, 5, 5, '2022-12-26 00:55:17', NULL, NULL),
(19, 16, 'Nhân Lê Khả', 6, 3, 8, 'Phòng Ngủ Đẹp', 'Phòng ngủ khách sạn đẹp, không gian thoải mái, nhân viên thân thiện.', 5, 5, 4, 4, 5, '2022-12-26 03:10:29', NULL, NULL),
(20, 17, 'Đà Nẵng Golden Bay', 8, 8, 8, 'Nơi Nghỉ Dưỡng Lý Tưởng', 'Khách sạn đẹp, phòng ốc rộng rãi, không gian thoải mái.', 5, 5, 5, 5, 5, '2022-12-26 05:25:42', NULL, NULL),
(27, 3, 'Customer 1', 2, 101, 201, 'Tốt', 'Khách sạn tốt, vị trí thuận lợi', 4, 5, 3, 4, 5, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(28, 5, 'Customer 2', 2, 102, 202, 'Ổn', 'Dịch vụ ổn nhưng cần cải thiện', 3, 3, 4, 3, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(29, 6, 'Customer 3', 2, 103, 203, 'Tuyệt vời', 'Khách sạn sạch sẽ và tiện nghi', 5, 5, 5, 5, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(30, 8, 'Customer 4', 2, 104, 204, 'Hài lòng', 'Dịch vụ tốt, nhân viên thân thiện', 4, 4, 4, 4, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(31, 9, 'Customer 5', 2, 105, 205, 'Giá tốt', 'Giá phòng hợp lý', 3, 3, 5, 4, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(32, 10, 'Customer 6', 2, 106, 206, 'Trung bình', 'Phòng hơi chật, tiện nghi chưa đầy đủ', 3, 2, 3, 3, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(33, 11, 'Customer 7', 2, 107, 207, 'Xuất sắc', 'Dịch vụ và vệ sinh tuyệt vời', 5, 5, 4, 5, 5, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(34, 12, 'Customer 8', 2, 108, 208, 'Thất vọng', 'Không gian không thoáng đãng', 2, 2, 3, 2, 2, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(35, 13, 'Customer 9', 2, 109, 209, 'Tốt', 'Gần trung tâm, tiện đi lại', 4, 4, 4, 4, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(36, 14, 'Customer 10', 2, 110, 210, 'Khá hài lòng', 'Nhân viên phục vụ tốt', 4, 3, 4, 4, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(37, 3, 'Customer 1', 3, 111, 211, 'Tốt', 'Khách sạn đẹp và sạch sẽ', 4, 4, 3, 5, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(38, 5, 'Customer 2', 3, 112, 212, 'Khá ổn', 'Dịch vụ ổn, giá hợp lý', 3, 3, 4, 3, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(39, 6, 'Customer 3', 3, 113, 213, 'Tuyệt vời', 'Dịch vụ tốt, vị trí thuận lợi', 5, 4, 5, 5, 5, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(40, 8, 'Customer 4', 3, 114, 214, 'Hài lòng', 'Tiện nghi đầy đủ, phục vụ tốt', 4, 4, 4, 4, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(41, 9, 'Customer 5', 3, 115, 215, 'Giá ổn', 'Phòng đẹp với mức giá phải chăng', 3, 3, 4, 4, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(42, 10, 'Customer 6', 3, 116, 216, 'Trung bình', 'Phòng hơi cũ, tiện nghi chưa đầy đủ', 3, 2, 3, 3, 3, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(43, 11, 'Customer 7', 3, 117, 217, 'Xuất sắc', 'Phòng đẹp, dịch vụ tuyệt vời', 5, 5, 4, 5, 5, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(44, 12, 'Customer 8', 3, 118, 218, 'Thất vọng', 'Không sạch sẽ như mong đợi', 2, 2, 3, 2, 2, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(45, 13, 'Customer 9', 3, 119, 219, 'Khá ổn', 'Gần trung tâm, tiện nghi đầy đủ', 4, 4, 4, 4, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(46, 14, 'Customer 10', 3, 120, 220, 'Hài lòng', 'Nhân viên phục vụ chu đáo', 4, 3, 4, 4, 4, '2024-11-04 13:50:16', '2024-11-04 13:50:16', NULL),
(47, 3, 'Customer 11', 17, 2, 3, 'Title 77', 'Content 52', 2, 1, 1, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(48, 16, 'Customer 10', 17, 5, 5, 'Title 17', 'Content 16', 2, 1, 2, 1, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(50, 13, 'Customer 6', 3, 7, 5, 'Title 89', 'Content 61', 2, 1, 1, 4, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(51, 5, 'Customer 3', 16, 5, 1, 'Title 75', 'Content 75', 3, 2, 5, 4, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(52, 17, 'Customer 5', 17, 4, 3, 'Title 14', 'Content 43', 4, 2, 4, 1, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(54, 3, 'Customer 16', 9, 3, 5, 'Title 4', 'Content 40', 5, 2, 5, 2, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(55, 8, 'Customer 17', 16, 8, 2, 'Title 86', 'Content 14', 1, 1, 3, 1, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(56, 17, 'Customer 17', 18, 4, 2, 'Title 25', 'Content 48', 4, 4, 5, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(57, 13, 'Customer 14', 18, 8, 2, 'Title 20', 'Content 16', 2, 4, 3, 2, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(58, 9, 'Customer 7', 3, 7, 4, 'Title 13', 'Content 28', 1, 2, 1, 1, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(59, 13, 'Customer 7', 10, 3, 5, 'Title 8', 'Content 49', 2, 4, 4, 5, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(62, 16, 'Customer 5', 6, 5, 4, 'Title 31', 'Content 33', 4, 4, 1, 5, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(63, 10, 'Customer 16', 4, 10, 3, 'Title 40', 'Content 63', 5, 5, 2, 2, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(64, 15, 'Customer 15', 11, 1, 5, 'Title 83', 'Content 78', 3, 4, 2, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(65, 13, 'Customer 3', 20, 6, 1, 'Title 85', 'Content 91', 1, 2, 2, 5, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(66, 8, 'Customer 6', 4, 1, 4, 'Title 39', 'Content 90', 2, 5, 2, 1, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(67, 14, 'Customer 6', 17, 3, 5, 'Title 34', 'Content 31', 3, 5, 3, 5, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(68, 12, 'Customer 15', 10, 7, 4, 'Title 1', 'Content 75', 4, 2, 4, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(69, 17, 'Customer 9', 7, 1, 2, 'Title 79', 'Content 83', 4, 3, 5, 5, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(71, 6, 'Customer 17', 2, 4, 4, 'Title 49', 'Content 31', 1, 3, 3, 3, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(72, 6, 'Customer 12', 13, 1, 2, 'Title 81', 'Content 93', 2, 2, 1, 1, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(73, 12, 'Customer 16', 16, 9, 1, 'Title 11', 'Content 16', 3, 5, 3, 2, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(74, 14, 'Customer 7', 7, 6, 5, 'Title 98', 'Content 13', 4, 1, 4, 1, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(75, 12, 'Customer 14', 2, 7, 1, 'Title 87', 'Content 88', 5, 3, 4, 3, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(76, 13, 'Customer 5', 15, 1, 5, 'Title 76', 'Content 93', 3, 2, 5, 3, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(79, 16, 'Customer 8', 8, 5, 2, 'Title 21', 'Content 11', 5, 2, 4, 4, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(80, 6, 'Customer 3', 12, 5, 3, 'Title 51', 'Content 91', 1, 2, 3, 5, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(81, 5, 'Customer 11', 9, 1, 2, 'Title 91', 'Content 92', 5, 3, 2, 3, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(83, 9, 'Customer 17', 11, 5, 5, 'Title 11', 'Content 87', 1, 3, 2, 2, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(84, 5, 'Customer 10', 5, 4, 1, 'Title 50', 'Content 23', 4, 4, 1, 1, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(85, 8, 'Customer 12', 2, 3, 2, 'Title 68', 'Content 53', 4, 3, 4, 4, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(86, 17, 'Customer 10', 10, 8, 2, 'Title 40', 'Content 8', 2, 4, 2, 1, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(87, 6, 'Customer 4', 18, 7, 1, 'Title 24', 'Content 1', 2, 3, 1, 2, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(88, 14, 'Customer 10', 5, 5, 5, 'Title 87', 'Content 78', 2, 1, 1, 4, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(89, 16, 'Customer 13', 16, 5, 2, 'Title 21', 'Content 4', 3, 5, 2, 5, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(90, 3, 'Customer 5', 14, 8, 4, 'Title 30', 'Content 45', 2, 3, 1, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(91, 17, 'Customer 3', 10, 10, 4, 'Title 20', 'Content 15', 1, 2, 1, 1, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(92, 14, 'Customer 3', 18, 1, 4, 'Title 27', 'Content 36', 5, 5, 3, 3, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(93, 3, 'Customer 11', 16, 9, 1, 'Title 11', 'Content 15', 3, 4, 3, 5, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(94, 3, 'Customer 8', 17, 7, 1, 'Title 76', 'Content 33', 2, 5, 1, 3, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(95, 17, 'Customer 10', 15, 9, 2, 'Title 21', 'Content 93', 1, 2, 4, 4, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(96, 5, 'Customer 15', 12, 3, 3, 'Title 51', 'Content 30', 5, 5, 4, 4, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(98, 12, 'Customer 14', 4, 3, 4, 'Title 18', 'Content 60', 3, 3, 3, 4, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(99, 9, 'Customer 15', 21, 2, 1, 'Title 7', 'Content 96', 3, 1, 3, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(101, 3, 'Customer 11', 14, 5, 3, 'Title 5', 'Content 79', 5, 4, 5, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(102, 5, 'Customer 3', 18, 1, 3, 'Title 58', 'Content 37', 1, 3, 5, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(103, 10, 'Customer 7', 21, 10, 5, 'Title 53', 'Content 4', 4, 5, 5, 3, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(104, 15, 'Customer 16', 2, 4, 4, 'Title 54', 'Content 55', 1, 1, 4, 1, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(105, 17, 'Customer 6', 5, 3, 4, 'Title 17', 'Content 47', 5, 5, 5, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(106, 6, 'Customer 9', 10, 8, 4, 'Title 23', 'Content 2', 3, 1, 1, 3, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(108, 5, 'Customer 17', 13, 9, 4, 'Title 53', 'Content 78', 2, 2, 1, 1, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(109, 9, 'Customer 3', 21, 7, 3, 'Title 82', 'Content 36', 2, 4, 1, 3, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(110, 3, 'Customer 9', 6, 8, 1, 'Title 2', 'Content 97', 4, 1, 4, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(111, 10, 'Customer 6', 13, 4, 5, 'Title 87', 'Content 41', 3, 1, 5, 3, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(112, 12, 'Customer 15', 11, 8, 2, 'Title 18', 'Content 9', 5, 2, 3, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(114, 10, 'Customer 16', 19, 7, 4, 'Title 34', 'Content 74', 4, 2, 3, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(115, 5, 'Customer 7', 18, 4, 2, 'Title 81', 'Content 87', 5, 1, 3, 3, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(116, 5, 'Customer 13', 3, 3, 1, 'Title 94', 'Content 24', 2, 1, 4, 5, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(118, 15, 'Customer 14', 9, 7, 5, 'Title 66', 'Content 61', 1, 4, 1, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(119, 5, 'Customer 7', 20, 9, 3, 'Title 49', 'Content 27', 5, 3, 2, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(120, 14, 'Customer 10', 8, 2, 4, 'Title 20', 'Content 85', 4, 4, 2, 2, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(121, 9, 'Customer 15', 19, 9, 4, 'Title 50', 'Content 74', 1, 4, 4, 4, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(122, 14, 'Customer 3', 19, 3, 3, 'Title 22', 'Content 38', 2, 1, 4, 3, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(123, 6, 'Customer 7', 21, 10, 5, 'Title 27', 'Content 88', 4, 3, 2, 4, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(124, 8, 'Customer 7', 11, 6, 1, 'Title 73', 'Content 50', 2, 2, 1, 5, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(125, 8, 'Customer 16', 11, 6, 2, 'Title 55', 'Content 10', 5, 1, 4, 2, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(126, 10, 'Customer 8', 10, 1, 1, 'Title 89', 'Content 42', 3, 5, 2, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(127, 12, 'Customer 15', 7, 9, 3, 'Title 89', 'Content 97', 1, 5, 2, 3, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(128, 17, 'Customer 15', 6, 7, 3, 'Title 72', 'Content 0', 5, 2, 5, 5, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(129, 6, 'Customer 11', 19, 9, 4, 'Title 53', 'Content 79', 2, 3, 2, 2, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(130, 10, 'Customer 8', 7, 3, 2, 'Title 24', 'Content 5', 3, 3, 5, 2, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(132, 12, 'Customer 17', 20, 9, 2, 'Title 43', 'Content 0', 4, 3, 3, 1, 1, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(133, 6, 'Customer 15', 7, 10, 5, 'Title 89', 'Content 62', 3, 2, 3, 5, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(134, 17, 'Customer 4', 10, 9, 5, 'Title 85', 'Content 69', 5, 2, 1, 4, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(135, 8, 'Customer 17', 13, 1, 3, 'Title 52', 'Content 0', 3, 2, 5, 1, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(138, 3, 'Customer 3', 3, 3, 5, 'Title 82', 'Content 44', 4, 2, 3, 3, 4, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(139, 15, 'Customer 6', 18, 4, 1, 'Title 79', 'Content 53', 2, 5, 2, 2, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(140, 16, 'Customer 12', 13, 10, 5, 'Title 37', 'Content 42', 5, 4, 2, 3, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(142, 5, 'Customer 6', 10, 6, 3, 'Title 47', 'Content 12', 1, 3, 5, 2, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(144, 9, 'Customer 15', 20, 2, 1, 'Title 24', 'Content 71', 5, 1, 5, 3, 2, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(145, 8, 'Customer 15', 3, 9, 1, 'Title 93', 'Content 34', 5, 3, 1, 1, 5, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(146, 3, 'Customer 12', 20, 9, 2, 'Title 35', 'Content 66', 2, 2, 3, 2, 3, '2024-11-04 13:53:33', '2024-11-04 13:53:33', NULL),
(174, 13, 'Customer 13', 10, 10, 2, 'Title 7', 'Content 29', 2, 2, 5, 2, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(175, 15, 'Customer 12', 15, 4, 5, 'Title 72', 'Content 67', 2, 1, 4, 2, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(176, 13, 'Customer 14', 16, 5, 2, 'Title 53', 'Content 9', 5, 5, 1, 4, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(178, 15, 'Customer 16', 21, 2, 4, 'Title 52', 'Content 27', 5, 2, 5, 2, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(180, 5, 'Customer 6', 16, 9, 1, 'Title 95', 'Content 48', 3, 2, 5, 3, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(181, 15, 'Customer 11', 5, 4, 1, 'Title 90', 'Content 96', 1, 3, 2, 1, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(182, 12, 'Customer 12', 9, 10, 3, 'Title 73', 'Content 19', 4, 2, 4, 2, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(183, 9, 'Customer 17', 13, 10, 5, 'Title 11', 'Content 59', 4, 3, 4, 4, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(184, 16, 'Customer 7', 17, 10, 4, 'Title 10', 'Content 69', 1, 4, 4, 5, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(185, 15, 'Customer 15', 18, 6, 2, 'Title 80', 'Content 13', 2, 1, 2, 5, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(186, 9, 'Customer 7', 7, 6, 5, 'Title 66', 'Content 74', 4, 3, 5, 4, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(187, 12, 'Customer 16', 14, 5, 1, 'Title 61', 'Content 56', 5, 2, 1, 5, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(188, 15, 'Customer 6', 15, 6, 5, 'Title 90', 'Content 73', 5, 4, 2, 4, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(190, 12, 'Customer 5', 5, 2, 3, 'Title 69', 'Content 12', 3, 2, 5, 4, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(191, 11, 'Customer 12', 13, 9, 3, 'Title 24', 'Content 54', 5, 2, 2, 5, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(192, 15, 'Customer 12', 15, 5, 2, 'Title 37', 'Content 80', 5, 5, 2, 2, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(194, 10, 'Customer 7', 21, 10, 4, 'Title 84', 'Content 5', 4, 3, 4, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(195, 17, 'Customer 9', 7, 1, 2, 'Title 72', 'Content 53', 3, 5, 2, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(196, 11, 'Customer 16', 15, 7, 2, 'Title 71', 'Content 53', 3, 1, 1, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(197, 17, 'Customer 11', 18, 7, 4, 'Title 22', 'Content 26', 4, 2, 1, 1, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(198, 14, 'Customer 17', 14, 2, 1, 'Title 66', 'Content 16', 5, 4, 2, 3, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(199, 11, 'Customer 13', 16, 5, 5, 'Title 73', 'Content 66', 1, 4, 1, 3, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(200, 14, 'Customer 15', 16, 1, 1, 'Title 70', 'Content 0', 5, 4, 2, 4, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(202, 9, 'Customer 14', 9, 8, 2, 'Title 78', 'Content 76', 3, 1, 5, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(203, 3, 'Customer 13', 12, 5, 4, 'Title 53', 'Content 29', 5, 3, 3, 4, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(204, 15, 'Customer 10', 20, 1, 4, 'Title 98', 'Content 98', 5, 1, 1, 3, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(205, 16, 'Customer 11', 3, 9, 4, 'Title 33', 'Content 44', 2, 4, 5, 3, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(206, 5, 'Customer 8', 5, 10, 1, 'Title 74', 'Content 40', 4, 4, 1, 2, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(208, 8, 'Customer 11', 16, 1, 5, 'Title 84', 'Content 24', 4, 4, 4, 5, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(209, 14, 'Customer 3', 19, 4, 1, 'Title 58', 'Content 54', 5, 2, 2, 2, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(210, 10, 'Customer 7', 19, 5, 4, 'Title 9', 'Content 39', 4, 2, 3, 3, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(211, 10, 'Customer 8', 10, 2, 2, 'Title 18', 'Content 99', 2, 1, 5, 1, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(212, 10, 'Customer 6', 14, 6, 4, 'Title 7', 'Content 19', 4, 1, 1, 2, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(213, 17, 'Customer 17', 19, 6, 1, 'Title 19', 'Content 45', 4, 1, 1, 1, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(214, 13, 'Customer 17', 15, 7, 1, 'Title 47', 'Content 13', 2, 5, 4, 3, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(215, 14, 'Customer 15', 2, 5, 2, 'Title 5', 'Content 38', 4, 5, 4, 4, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(216, 14, 'Customer 12', 21, 10, 1, 'Title 12', 'Content 57', 3, 4, 3, 4, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(217, 9, 'Customer 16', 5, 4, 5, 'Title 71', 'Content 81', 5, 1, 5, 3, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(218, 5, 'Customer 5', 11, 8, 1, 'Title 76', 'Content 29', 1, 1, 3, 4, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(220, 14, 'Customer 7', 9, 9, 1, 'Title 66', 'Content 24', 2, 2, 5, 5, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(221, 17, 'Customer 12', 7, 4, 1, 'Title 77', 'Content 30', 2, 1, 5, 1, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(222, 3, 'Customer 15', 21, 5, 1, 'Title 55', 'Content 31', 5, 3, 5, 1, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(223, 15, 'Customer 10', 5, 3, 5, 'Title 44', 'Content 68', 1, 3, 5, 2, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(225, 16, 'Customer 10', 18, 6, 3, 'Title 62', 'Content 68', 3, 4, 1, 2, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(226, 11, 'Customer 16', 15, 9, 1, 'Title 36', 'Content 28', 2, 4, 3, 2, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(227, 3, 'Customer 9', 4, 4, 2, 'Title 18', 'Content 22', 3, 2, 3, 4, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(230, 5, 'Customer 5', 12, 10, 2, 'Title 56', 'Content 96', 1, 4, 3, 3, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(231, 16, 'Customer 12', 7, 5, 3, 'Title 28', 'Content 81', 2, 4, 5, 1, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(232, 13, 'Customer 13', 9, 8, 4, 'Title 33', 'Content 48', 3, 4, 3, 3, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(233, 15, 'Customer 6', 16, 10, 3, 'Title 35', 'Content 50', 3, 4, 5, 5, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(234, 13, 'Customer 15', 19, 1, 3, 'Title 41', 'Content 55', 3, 1, 4, 1, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(235, 8, 'Customer 10', 12, 1, 5, 'Title 86', 'Content 83', 3, 3, 4, 4, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(236, 12, 'Customer 4', 15, 2, 4, 'Title 61', 'Content 27', 3, 5, 3, 1, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(237, 12, 'Customer 3', 5, 7, 5, 'Title 39', 'Content 31', 3, 1, 3, 2, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(238, 6, 'Customer 17', 4, 8, 3, 'Title 6', 'Content 89', 2, 4, 4, 1, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(239, 9, 'Customer 6', 21, 2, 4, 'Title 77', 'Content 99', 4, 2, 4, 1, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(240, 9, 'Customer 16', 4, 10, 2, 'Title 93', 'Content 62', 2, 4, 4, 4, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(241, 8, 'Customer 8', 17, 7, 5, 'Title 63', 'Content 44', 2, 2, 2, 5, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(242, 16, 'Customer 7', 17, 10, 2, 'Title 45', 'Content 56', 3, 3, 3, 1, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(243, 14, 'Customer 12', 20, 8, 5, 'Title 55', 'Content 88', 4, 1, 3, 2, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(245, 5, 'Customer 8', 8, 6, 4, 'Title 91', 'Content 46', 3, 3, 1, 3, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(246, 10, 'Customer 3', 14, 1, 2, 'Title 78', 'Content 76', 3, 1, 4, 3, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(247, 12, 'Customer 16', 13, 2, 1, 'Title 89', 'Content 25', 3, 1, 4, 3, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(248, 16, 'Customer 14', 3, 10, 4, 'Title 53', 'Content 59', 2, 1, 2, 4, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(249, 12, 'Customer 14', 2, 8, 4, 'Title 42', 'Content 89', 1, 2, 5, 5, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(250, 11, 'Customer 9', 13, 7, 2, 'Title 75', 'Content 78', 4, 1, 3, 5, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(251, 14, 'Customer 5', 15, 9, 1, 'Title 12', 'Content 23', 5, 2, 2, 2, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(252, 8, 'Customer 4', 8, 6, 3, 'Title 25', 'Content 59', 2, 2, 4, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(253, 14, 'Customer 12', 16, 9, 1, 'Title 19', 'Content 46', 4, 2, 2, 3, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(255, 8, 'Customer 15', 5, 4, 1, 'Title 74', 'Content 26', 1, 4, 2, 1, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(256, 14, 'Customer 15', 20, 1, 2, 'Title 71', 'Content 51', 3, 3, 2, 1, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(257, 14, 'Customer 7', 4, 9, 4, 'Title 18', 'Content 70', 5, 4, 5, 2, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(259, 6, 'Customer 7', 19, 6, 1, 'Title 98', 'Content 50', 3, 2, 5, 2, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(260, 16, 'Customer 9', 11, 10, 2, 'Title 98', 'Content 81', 1, 1, 2, 5, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(261, 10, 'Customer 15', 14, 8, 4, 'Title 42', 'Content 98', 4, 2, 3, 3, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(262, 9, 'Customer 15', 19, 10, 1, 'Title 57', 'Content 63', 3, 2, 2, 3, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(263, 8, 'Customer 11', 15, 7, 1, 'Title 51', 'Content 38', 2, 3, 5, 3, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(264, 5, 'Customer 5', 6, 6, 2, 'Title 91', 'Content 55', 1, 2, 5, 2, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(265, 11, 'Customer 5', 2, 7, 1, 'Title 2', 'Content 53', 3, 2, 5, 5, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(267, 8, 'Customer 6', 2, 5, 1, 'Title 32', 'Content 26', 2, 5, 3, 4, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(268, 16, 'Customer 11', 2, 5, 1, 'Title 91', 'Content 46', 4, 4, 2, 5, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(269, 15, 'Customer 12', 12, 9, 4, 'Title 93', 'Content 56', 1, 2, 5, 3, 2, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(270, 9, 'Customer 4', 4, 4, 1, 'Title 9', 'Content 85', 1, 3, 4, 3, 5, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(271, 12, 'Customer 10', 16, 1, 1, 'Title 48', 'Content 3', 4, 3, 1, 5, 1, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(272, 15, 'Customer 4', 19, 2, 1, 'Title 20', 'Content 60', 3, 2, 5, 1, 4, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL),
(273, 5, 'Customer 13', 21, 9, 3, 'Title 71', 'Content 11', 3, 5, 2, 4, 3, '2024-11-04 14:16:05', '2024-11-04 14:16:05', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_evaluate_restaurant`
--

CREATE TABLE `tbl_evaluate_restaurant` (
  `evaluate_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `customer_name` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `evaluate_title` varchar(255) NOT NULL,
  `evaluate_content` varchar(255) NOT NULL,
  `evaluate_service` int(11) NOT NULL,
  `evaluate_point` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_facilitieshotel`
--

CREATE TABLE `tbl_facilitieshotel` (
  `facilitieshotel_id` int(11) NOT NULL,
  `facilitieshotel_name` varchar(256) NOT NULL,
  `facilitieshotel_image` varchar(256) NOT NULL,
  `facilitieshotel_group` int(11) NOT NULL,
  `facilitieshotel_status` int(1) NOT NULL,
  `facilitieshotel_desc` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_facilitieshotel`
--

INSERT INTO `tbl_facilitieshotel` (`facilitieshotel_id`, `facilitieshotel_name`, `facilitieshotel_image`, `facilitieshotel_group`, `facilitieshotel_status`, `facilitieshotel_desc`, `created_at`, `updated_at`, `deleted_at`) VALUES
(2, 'Bãi Đậu Ô tô', 'car_for_hire47.png', 2, 1, 'Bãi Đậu Ô tô', '2022-11-14 13:51:41', '2022-11-14 14:36:30', NULL),
(3, 'Phòng Gym', 'gym83.png', 3, 1, 'Phòng Gym', '2022-11-14 14:19:05', NULL, NULL),
(4, 'Lễ Tân 24h', 'reception-hotel-24h65.svg', 4, 1, 'Lễ Tân 24h', '2022-11-14 14:19:34', NULL, NULL),
(5, 'Internet Miễn Phí', 'Amenities_wifi29.png', 5, 1, 'Internet Miễn Phí', '2022-11-14 14:20:07', NULL, NULL),
(6, 'Spa', 'spa-stone 128.png', 6, 1, 'Spa', '2022-11-14 14:20:33', NULL, NULL),
(7, 'Dọn Dẹp Hàng Ngày', 'don-dep-hang-ngay7.png', 7, 1, 'Dọn Dẹp Hàng Ngày', '2022-11-14 14:21:18', NULL, NULL),
(8, 'Lối Vào Người Khuyết Tật', 'loi-vao-xe-lan31.png', 8, 1, 'Lối Vào Người Khuyết Tật', '2022-11-14 14:21:57', NULL, NULL),
(9, 'Bồn Rữa Mặt Thấp', 'bon-rua-mat-thap-hon39.png', 8, 1, 'Bồn Rữa Mặt Thấp', '2022-11-14 14:23:24', NULL, NULL),
(10, 'Nhà Hàng', 'nha-hang95.png', 9, 1, 'Nhà Hàng', '2022-11-14 14:23:59', NULL, NULL),
(11, 'Phòng Họp', 'phong-hop9.png', 10, 1, 'Phòng Họp', '2022-11-14 14:24:56', NULL, NULL),
(12, 'Tổ Chức Sự Kiện', 'phong-hop90.png', 10, 1, 'Tổ Chức Sự Kiện', '2022-11-14 14:25:30', NULL, NULL),
(13, 'American Express', 'payment_jcb29.png', 1, 1, 'American Express', '2022-11-14 14:26:21', NULL, NULL),
(14, 'Máy Fax', 'printer 162.png', 10, 1, 'Máy Fax', '2022-11-14 14:27:26', NULL, NULL),
(15, 'Hồ bơi', 'swimming-pool-person 162.png', 12, 1, 'Hồ bơi', '2022-11-14 14:28:26', NULL, NULL),
(16, 'Sân Thượng', 'san-thuong11.png', 11, 1, 'Sân Thượng', '2022-11-14 14:28:57', NULL, NULL),
(17, 'Ban Công', 'balcony12.png', 11, 1, 'Ban Công', '2022-11-14 14:29:42', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_facilitiesroom`
--

CREATE TABLE `tbl_facilitiesroom` (
  `facilitiesroom_id` int(11) NOT NULL,
  `facilitiesroom_name` varchar(256) NOT NULL,
  `facilitiesroom_image` varchar(256) NOT NULL,
  `facilitiesroom_status` int(1) NOT NULL,
  `facilitiesroom_desc` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_facilitiesroom`
--

INSERT INTO `tbl_facilitiesroom` (`facilitiesroom_id`, `facilitiesroom_name`, `facilitiesroom_image`, `facilitiesroom_status`, `facilitiesroom_desc`, `created_at`, `updated_at`, `deleted_at`) VALUES
(2, 'Vòi Sen', 'voisen69.svg', 1, 'Vòi Sen', '2022-11-14 12:59:14', NULL, NULL),
(3, 'Truyền Hình', 'truyenhinh7.png', 1, 'Truyền Hình', '2022-11-14 12:59:40', NULL, NULL),
(4, 'Trà Cafe', 'tracafe68.svg', 1, 'Trà Cafe', '2022-11-14 13:00:05', NULL, NULL),
(5, 'Tivi', 'tivi72.svg', 1, 'Tivi', '2022-11-14 13:00:25', NULL, NULL),
(6, 'Nước', 'nuoc47.svg', 1, 'Nước', '2022-11-14 13:01:16', NULL, NULL),
(7, 'Máy Sấy', 'maysay22.svg', 1, 'Máy Sấy', '2022-11-14 13:01:35', NULL, NULL),
(8, 'Ghế Sofa', 'ghesofa73.svg', 1, 'Ghế Sofa', '2022-11-14 13:01:51', NULL, NULL),
(9, 'Đồ Vệ Sinh', 'dovesinh27.svg', 1, 'Đồ Vệ Sinh', '2022-11-14 13:02:10', NULL, NULL),
(10, 'Dọn Phòng', 'donphong12.png', 1, 'Dọn Phòng', '2022-11-14 13:02:30', NULL, NULL),
(11, 'Cửa Sổ', 'cuaso85.svg', 1, 'Cửa Sổ', '2022-11-14 13:02:49', NULL, NULL),
(12, 'Bình Nước', 'binhnuoc86.svg', 1, 'Bình Nước', '2022-11-14 13:03:10', NULL, NULL),
(13, 'Bàn Trang Điểm', 'bantrangdiem86.svg', 1, 'Bàn Trang Điểm', '2022-11-14 13:03:29', NULL, NULL),
(14, 'Wi-fi 5.0', 'wifi71.png', 1, 'Wi-fi 5', '2022-11-14 13:29:02', NULL, NULL),
(15, 'Bồn Rữa Mặt Thấp', 'bon-rua-mat-thap-hon3.png', 1, 'Bồn Rữa Mặt Thấp', '2022-11-14 14:22:31', '2022-11-14 14:22:44', '2022-11-14 07:22:44');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_gallery_hotel`
--

CREATE TABLE `tbl_gallery_hotel` (
  `gallery_hotel_id` int(11) NOT NULL,
  `hotel_id` int(11) NOT NULL,
  `gallery_hotel_name` varchar(256) NOT NULL,
  `gallery_hotel_type` int(1) NOT NULL,
  `gallery_hotel_image` varchar(256) NOT NULL,
  `gallery_hotel_content` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_gallery_hotel`
--

INSERT INTO `tbl_gallery_hotel` (`gallery_hotel_id`, `hotel_id`, `gallery_hotel_name`, `gallery_hotel_type`, `gallery_hotel_image`, `gallery_hotel_content`, `created_at`, `updated_at`) VALUES
(4, 2, '9B54DXB0GS_VPCRFDN_Facade2', 1, '35180_4YFAIH6OG5_VPCRFDN_Pool148.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', '2022-11-05 10:29:28'),
(5, 2, '35180_AESHFLUMK7_VPCRFDN_Lobby4', 1, '35180_AESHFLUMK7_VPCRFDN_Lobby429.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(6, 2, '35180_CVU7TYMVJ7_VPCRFDN_Lobby8', 1, '35180_CVU7TYMVJ7_VPCRFDN_Lobby811.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(7, 2, '35180_GTBQTXHE3C_VPCRFDN_Yoga2', 1, '35180_GTBQTXHE3C_VPCRFDN_Yoga291.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(8, 2, '35180_HCH9GIZ0QK_VPCRFDN_Facade1', 1, '35180_HCH9GIZ0QK_VPCRFDN_Facade125.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(9, 2, '35180_LKLH41D98X_VPCRFDN_Facade13', 1, '35180_LKLH41D98X_VPCRFDN_Facade1317.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(10, 2, '35180_SX9ZZ577PA_VPCRFDN_Facade9', 1, '35180_SX9ZZ577PA_VPCRFDN_Facade985.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(11, 2, '35180_U0CPD869LF_VPCRFDN_Landscape5', 1, '35180_U0CPD869LF_VPCRFDN_Landscape582.jpg', 'Ảnh này chưa có nội dung !', '2022-11-04 16:49:19', NULL),
(16, 2, '35180_MYTOUR', 2, '35180_MYTOUR9.mp4', 'Chưa có nội dung !', '2022-11-05 10:54:07', NULL),
(17, 3, '35180_2EJLPA5OE8_VPCRFDN_Lobby1', 1, '35180_2EJLPA5OE8_VPCRFDN_Lobby191.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(18, 3, '35180_4YFAIH6OG5_VPCRFDN_Pool1', 1, '35180_4YFAIH6OG5_VPCRFDN_Pool110.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(19, 3, '35180_7LZ992QP52_VPCRFDN_Lifestyle32', 1, '35180_7LZ992QP52_VPCRFDN_Lifestyle3275.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(20, 3, '35180_9B54DXB0GS_VPCRFDN_Facade2', 1, '35180_9B54DXB0GS_VPCRFDN_Facade241.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(21, 3, '35180_AESHFLUMK7_VPCRFDN_Lobby4', 1, '35180_AESHFLUMK7_VPCRFDN_Lobby437.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(22, 3, '35180_CVU7TYMVJ7_VPCRFDN_Lobby8', 1, '35180_CVU7TYMVJ7_VPCRFDN_Lobby834.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(23, 3, '35180_GTBQTXHE3C_VPCRFDN_Yoga2', 1, '35180_GTBQTXHE3C_VPCRFDN_Yoga257.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(24, 3, '35180_HCH9GIZ0QK_VPCRFDN_Facade1', 1, '35180_HCH9GIZ0QK_VPCRFDN_Facade166.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(25, 3, '35180_LKLH41D98X_VPCRFDN_Facade13', 1, '35180_LKLH41D98X_VPCRFDN_Facade1361.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(26, 3, '35180_SX9ZZ577PA_VPCRFDN_Facade9', 1, '35180_SX9ZZ577PA_VPCRFDN_Facade972.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(27, 3, '35180_U0CPD869LF_VPCRFDN_Landscape5', 1, '35180_U0CPD869LF_VPCRFDN_Landscape50.jpg', 'Chưa có nội dung !', '2022-11-05 14:51:59', NULL),
(28, 3, '35180_W5O58G8TK7_VPCRFDN_Facade3', 1, '35180_W5O58G8TK7_VPCRFDN_Facade373.jpg', 'Chưa có nội dung !', '2022-11-05 14:52:00', NULL),
(29, 3, '35180_Y2CJGBZMF6_VPCRFDN_Facade7', 1, '35180_Y2CJGBZMF6_VPCRFDN_Facade725.jpg', 'Chưa có nội dung !', '2022-11-05 14:52:00', NULL),
(30, 3, '35180_MYTOUR', 2, '35180_MYTOUR66.mp4', 'Chưa có nội dung !', '2022-11-05 14:52:11', NULL),
(31, 4, '35336_MYTOUR', 2, '35336_MYTOUR21.mp4', 'Chưa có nội dung !', '2022-11-06 08:42:44', NULL),
(32, 4, '0f9f0b55266cebeabcf6ed7ba14fad24', 1, '0f9f0b55266cebeabcf6ed7ba14fad2443.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(33, 4, '2_142801_02', 1, '2_142801_0285.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(34, 4, '253367671', 1, '25336767111.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(35, 4, '253367672', 1, '25336767284.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(36, 4, 'image-8', 1, 'image-823.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(37, 4, 'image-9', 1, 'image-925.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(38, 4, 'image-10', 1, 'image-1038.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(39, 4, 'image-12', 1, 'image-1261.jpg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(40, 4, 'ppsAaNtpTZ_sTTydPkiqsA-6', 1, 'ppsAaNtpTZ_sTTydPkiqsA-66.jpeg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(41, 4, 'STv5GmFzSFK9_sDyWZtz8w-21', 1, 'STv5GmFzSFK9_sDyWZtz8w-2112.jpeg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(42, 4, 't7m0SzyZSzemAqP5lmJ2Ww-37', 1, 't7m0SzyZSzemAqP5lmJ2Ww-371.jpeg', 'Chưa có nội dung !', '2022-11-06 08:43:07', NULL),
(43, 5, '_KgSKL9jQ8mm-myNc9ZVww-84', 1, '_KgSKL9jQ8mm-myNc9ZVww-8482.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(44, 5, '_KgSKL9jQ8mm-myNc9ZVww-99', 1, '_KgSKL9jQ8mm-myNc9ZVww-9991.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(45, 5, '09f2f6eadd73be726c0d86f64c900997', 1, '09f2f6eadd73be726c0d86f64c90099732.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(46, 5, '17c6760c7a281e208fddb0bf9e256d1e', 1, '17c6760c7a281e208fddb0bf9e256d1e36.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(47, 5, '17eb252deab29e1e04d4a2b3f66b5595', 1, '17eb252deab29e1e04d4a2b3f66b559587.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(48, 5, '171409520', 1, '17140952099.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(49, 5, '178962862', 1, '17896286234.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(50, 5, '178964092', 1, '17896409295.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(51, 5, '179246990', 1, '17924699052.jpg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(52, 5, 'bwGZioIlSz6QQ-ebzJvfcQ-225', 1, 'bwGZioIlSz6QQ-ebzJvfcQ-22517.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(53, 5, 'RMAzmAy-SXG_JL-z9lXnmA-36', 1, 'RMAzmAy-SXG_JL-z9lXnmA-3620.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(54, 5, 'RMAzmAy-SXG_JL-z9lXnmA-42', 1, 'RMAzmAy-SXG_JL-z9lXnmA-4269.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(55, 5, 'RMAzmAy-SXG_JL-z9lXnmA-51', 1, 'RMAzmAy-SXG_JL-z9lXnmA-5110.jpeg', 'Chưa có nội dung !', '2022-11-06 08:45:57', NULL),
(56, 5, '35122_MYTOUR', 2, '35122_MYTOUR38.mp4', 'Chưa có nội dung !', '2022-11-06 08:46:06', NULL),
(57, 6, '1299_MYTOUR', 2, '1299_MYTOUR15.mp4', 'Chưa có nội dung !', '2022-12-23 08:27:15', NULL),
(58, 6, '4TeHzNe-SUu9n3qYO900Sw-26', 1, '4TeHzNe-SUu9n3qYO900Sw-2664.jpeg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(59, 6, '7r71534936465_khach_san_grand_tourane', 1, '7r71534936465_khach_san_grand_tourane71.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(60, 6, '1158339_16042211100041707204', 1, '1158339_1604221110004170720428.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(61, 6, 'apr-26-edited-grand-tourane-room-1', 1, 'apr-26-edited-grand-tourane-room-132.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(62, 6, 'dsc00808-edit', 1, 'dsc00808-edit32.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(63, 6, 'dsc01906-fix', 1, 'dsc01906-fix56.jfif', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(64, 6, 'dsc02322', 1, 'dsc0232226.jfif', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(65, 6, 'grandspa-7', 1, 'grandspa-772.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(66, 6, 'jun20---grand-tourane---edit-beach-2', 1, 'jun20---grand-tourane---edit-beach-259.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(67, 6, 'kfh1534936468_khach_san_grand_tourane', 1, 'kfh1534936468_khach_san_grand_tourane17.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(68, 6, 'y751534936469_khach_san_grand_tourane', 1, 'y751534936469_khach_san_grand_tourane97.jpg', 'Chưa có nội dung !', '2022-12-23 08:29:03', NULL),
(92, 8, '1285_MYTOUR', 2, '1285_MYTOUR19.mp4', 'Chưa có nội dung !', '2022-12-23 09:03:43', NULL),
(93, 8, '215171431', 1, '2151714319.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(94, 8, '215171534', 1, '21517153479.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(95, 8, '215171539', 1, '21517153929.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(96, 8, '215171553', 1, '2151715530.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(97, 8, '215171561', 1, '2151715615.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(98, 8, '215173153', 1, '2151731532.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(99, 8, '215176383', 1, '21517638339.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(100, 8, '215176469', 1, '21517646999.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(101, 8, '215176485 (1)', 1, '215176485 (1)86.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(102, 8, '215176485', 1, '2151764850.jpg', 'Chưa có nội dung !', '2022-12-23 09:03:53', NULL),
(115, 9, '1162_MYTOUR', 2, '1162_MYTOUR29.mp4', 'Chưa có nội dung !', '2022-12-23 13:34:42', NULL),
(116, 9, '2-1', 1, '2-139.png', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(117, 9, '6-2', 1, '6-269.png', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(118, 9, '277707865', 1, '27770786555.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(119, 9, '277707879', 1, '27770787926.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(120, 9, '277707916', 1, '27770791648.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(121, 9, '277707956', 1, '27770795630.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(122, 9, '277707987', 1, '27770798745.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(123, 9, 'deluxe---king-43', 1, 'deluxe---king-4335.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(124, 9, 'family---king-_-twin-13', 1, 'family---king-_-twin-1373.jpg', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(125, 9, 'main-picture', 1, 'main-picture16.png', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(126, 9, 'untitled', 1, 'untitled31.png', 'Chưa có nội dung !', '2022-12-23 13:35:06', NULL),
(150, 12, '4822_MYTOUR', 2, '4822_MYTOUR84.mp4', 'Chưa có nội dung !', '2022-12-23 18:43:09', NULL),
(151, 12, '5ab95879', 1, '5ab9587963.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(152, 12, 'c4ac777b', 1, 'c4ac777b11.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(153, 12, 'e2597441', 1, 'e259744125.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(154, 12, 'ogWWkkuvRcOy-lO07FVY5Q-0', 1, 'ogWWkkuvRcOy-lO07FVY5Q-028.jpeg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(155, 12, 'oz9ShyIiRES4d_rS8cbx_Q-2', 1, 'oz9ShyIiRES4d_rS8cbx_Q-21.jpeg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(156, 12, 'z6XSSQtfRXaEP_W-Zvu-cg-13', 1, 'z6XSSQtfRXaEP_W-Zvu-cg-1372.jpeg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(157, 12, 'z3853685949505_1fee13e181aa11d21e6a45ddcb6c09ba', 1, 'z3853685949505_1fee13e181aa11d21e6a45ddcb6c09ba52.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(158, 12, 'z3903433323344_6bbb910d79ab546e087e0d7bcf76e7fb', 1, 'z3903433323344_6bbb910d79ab546e087e0d7bcf76e7fb82.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(159, 12, 'z3903433366364_a5d2f02cbf261ab4019f48119b5c0247', 1, 'z3903433366364_a5d2f02cbf261ab4019f48119b5c024732.jpg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(160, 12, 'ZYlHjDlcQouL6WMoOrKZlg-1', 1, 'ZYlHjDlcQouL6WMoOrKZlg-131.jpeg', 'Chưa có nội dung !', '2022-12-23 18:43:59', NULL),
(161, 13, '29432_MYTOUR', 2, '29432_MYTOUR43.mp4', 'Chưa có nội dung !', '2022-12-23 18:53:55', NULL),
(162, 13, '139587411', 1, '13958741175.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(163, 13, '139590744', 1, '13959074446.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(164, 13, '139590752-1', 1, '139590752-127.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(165, 13, '139590793', 1, '13959079314.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(166, 13, '139591409', 1, '13959140957.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(167, 13, '139591411', 1, '13959141135.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(168, 13, '159472672', 1, '15947267226.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(169, 13, '159472678 (1)', 1, '159472678 (1)15.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(170, 13, '159472678', 1, '1594726782.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(171, 13, '226582810', 1, '22658281064.jpg', 'Chưa có nội dung !', '2022-12-23 18:54:45', NULL),
(172, 14, '29432_MYTOUR', 2, '29432_MYTOUR37.mp4', 'Chưa có nội dung !', '2022-12-23 19:03:40', NULL),
(173, 14, '1', 1, '137.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(174, 14, '2', 1, '214.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(175, 14, '3', 1, '312.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(176, 14, '4', 1, '455.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(177, 14, '5', 1, '547.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(178, 14, '7', 1, '711.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(179, 14, '8', 1, '854.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(180, 14, '9', 1, '97.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(181, 14, '10', 1, '1035.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(182, 14, '11', 1, '1138.jpg', 'Chưa có nội dung !', '2022-12-23 19:04:38', NULL),
(209, 17, '29403_MYTOUR', 2, '29403_MYTOUR43.mp4', 'Chưa có nội dung !', '2022-12-24 02:51:39', NULL),
(210, 17, '7bx1528889526_da_nang_golden_bay', 1, '7bx1528889526_da_nang_golden_bay72.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(211, 17, '29403_35AR53UY5W_28', 1, '29403_35AR53UY5W_2845.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(212, 17, '29403_91NIZUCJER_22', 1, '29403_91NIZUCJER_2252.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(213, 17, '29403_FE9FI9AMFU_24', 1, '29403_FE9FI9AMFU_2442.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(214, 17, '29403_QGEQ43WK47_27', 1, '29403_QGEQ43WK47_271.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(215, 17, '3471357_17112210380059706121', 1, '3471357_171122103800597061219.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(216, 17, 'eja1528889594_da_nang_golden_bay', 1, 'eja1528889594_da_nang_golden_bay69.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(217, 17, 'mfr1528889512_da_nang_golden_bay', 1, 'mfr1528889512_da_nang_golden_bay83.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(218, 17, 'ps91528889525_da_nang_golden_bay', 1, 'ps91528889525_da_nang_golden_bay36.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(219, 17, 'sap1541676224_da_nang_golden_bay', 1, 'sap1541676224_da_nang_golden_bay11.jpg', 'Chưa có nội dung !', '2022-12-24 02:51:48', NULL),
(220, 18, '1162_MYTOUR', 2, '1162_MYTOUR86.mp4', 'Chưa có nội dung !', '2022-12-24 02:59:52', NULL),
(221, 18, '_dhp2798-a', 1, '_dhp2798-a63.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(222, 18, '_dhp2954-copy', 1, '_dhp2954-copy0.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(223, 18, '21', 1, '2160.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(224, 18, '255913883', 1, '25591388378.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(225, 18, 'cb50360f', 1, 'cb50360f88.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(226, 18, 'cici', 1, 'cici76.jpg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(227, 18, 'ES9WIGpST-SXFNLIUU-QWw-33', 1, 'ES9WIGpST-SXFNLIUU-QWw-3320.jpeg', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(229, 18, 'RNHt9A8rSpKj4aGvKosNug-91', 1, 'RNHt9A8rSpKj4aGvKosNug-918.png', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(230, 18, 'RNHt9A8rSpKj4aGvKosNug-92', 1, 'RNHt9A8rSpKj4aGvKosNug-9232.png', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(231, 18, 'ROUfOOdJQgyXUxpq_uSqSQ-183', 1, 'ROUfOOdJQgyXUxpq_uSqSQ-18321.png', 'Chưa có nội dung !', '2022-12-24 03:00:05', NULL),
(232, 19, '35209_MYTOUR', 2, '35209_MYTOUR13.mp4', 'Chưa có nội dung !', '2022-12-24 03:09:21', NULL),
(233, 19, 'entrance2', 1, 'entrance230.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(234, 19, 'entrance5', 1, 'entrance519.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(235, 19, 'entrance6-1', 1, 'entrance6-137.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(236, 19, 'entrance-passage3', 1, 'entrance-passage337.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(237, 19, 'entrance-passage4', 1, 'entrance-passage457.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(238, 19, 'gate2', 1, 'gate25.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(239, 19, 'outdoor-restrant4', 1, 'outdoor-restrant484.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(240, 19, 'pooiside3-1', 1, 'pooiside3-196.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(241, 19, 'pooiside9', 1, 'pooiside90.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(242, 19, 'poolside2', 1, 'poolside21.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(243, 19, 'poolside8-2', 1, 'poolside8-233.jpeg', 'Chưa có nội dung !', '2022-12-24 03:09:34', NULL),
(264, 21, '_dhp2798-a', 1, '_dhp2798-a64.jpg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(265, 21, '_dhp2954-copy', 1, '_dhp2954-copy76.jpg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(266, 21, '21', 1, '2181.jpg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(267, 21, '255913883', 1, '25591388387.jpg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(268, 21, 'ES9WIGpST-SXFNLIUU-QWw-33', 1, 'ES9WIGpST-SXFNLIUU-QWw-3350.jpeg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(269, 21, 'KLvvoKKZTh_dhmTrzI-i5w-291-gym%20rs', 1, 'KLvvoKKZTh_dhmTrzI-i5w-291-gym%20rs23.jpeg', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(270, 21, 'RNHt9A8rSpKj4aGvKosNug-91', 1, 'RNHt9A8rSpKj4aGvKosNug-9128.png', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(271, 21, 'RNHt9A8rSpKj4aGvKosNug-92', 1, 'RNHt9A8rSpKj4aGvKosNug-9286.png', 'Chưa có nội dung !', '2022-12-24 03:35:49', NULL),
(272, 21, '8', 2, '84.mp4', 'Chưa có nội dung !', '2022-12-24 03:36:31', NULL),
(273, 20, '8', 2, '886.mp4', 'Chưa có nội dung !', '2022-12-24 03:37:27', NULL),
(274, 20, '2-1', 1, '2-149.png', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(275, 20, '6-2', 1, '6-286.png', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(276, 20, '277707865', 1, '27770786596.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(277, 20, '277707879', 1, '27770787917.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(278, 20, '277707916', 1, '27770791659.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(279, 20, '277707956', 1, '27770795618.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(280, 20, '277707987', 1, '27770798774.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(281, 20, 'deluxe---king-43', 1, 'deluxe---king-4333.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(282, 20, 'family---king-_-twin-13', 1, 'family---king-_-twin-1377.jpg', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(283, 20, 'main-picture', 1, 'main-picture29.png', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(284, 20, 'untitled', 1, 'untitled49.png', 'Chưa có nội dung !', '2022-12-24 03:38:11', NULL),
(285, 16, '4TeHzNe-SUu9n3qYO900Sw-26', 1, '4TeHzNe-SUu9n3qYO900Sw-2637.jpeg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(286, 16, '7r71534936465_khach_san_grand_tourane', 1, '7r71534936465_khach_san_grand_tourane9.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(287, 16, '1158339_16042211100041707204', 1, '1158339_1604221110004170720456.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(288, 16, 'apr-26-edited-grand-tourane-room-1', 1, 'apr-26-edited-grand-tourane-room-194.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(289, 16, 'dsc00808-edit', 1, 'dsc00808-edit26.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(290, 16, 'dsc01906-fix', 1, 'dsc01906-fix76.jfif', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(291, 16, 'dsc02322', 1, 'dsc0232285.jfif', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(292, 16, 'grandspa-7', 1, 'grandspa-750.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(293, 16, 'jun20---grand-tourane---edit-beach-2', 1, 'jun20---grand-tourane---edit-beach-226.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(294, 16, 'kfh1534936468_khach_san_grand_tourane', 1, 'kfh1534936468_khach_san_grand_tourane9.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(295, 16, 'y751534936469_khach_san_grand_tourane', 1, 'y751534936469_khach_san_grand_tourane92.jpg', 'Chưa có nội dung !', '2022-12-24 03:40:57', NULL),
(296, 16, '2', 2, '238.mp4', 'Chưa có nội dung !', '2022-12-24 03:41:19', NULL),
(297, 15, '2', 2, '236.mp4', 'Chưa có nội dung !', '2022-12-24 03:41:52', NULL),
(298, 15, '4TeHzNe-SUu9n3qYO900Sw-26', 1, '4TeHzNe-SUu9n3qYO900Sw-2632.jpeg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(299, 15, '7r71534936465_khach_san_grand_tourane', 1, '7r71534936465_khach_san_grand_tourane73.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(300, 15, '1158339_16042211100041707204', 1, '1158339_1604221110004170720434.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(301, 15, 'apr-26-edited-grand-tourane-room-1', 1, 'apr-26-edited-grand-tourane-room-129.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(302, 15, 'dsc00808-edit', 1, 'dsc00808-edit5.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(303, 15, 'dsc01906-fix', 1, 'dsc01906-fix0.jfif', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(304, 15, 'dsc02322', 1, 'dsc0232221.jfif', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(305, 15, 'grandspa-7', 1, 'grandspa-758.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(306, 15, 'jun20---grand-tourane---edit-beach-2', 1, 'jun20---grand-tourane---edit-beach-255.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(307, 15, 'kfh1534936468_khach_san_grand_tourane', 1, 'kfh1534936468_khach_san_grand_tourane39.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(308, 15, 'y751534936469_khach_san_grand_tourane', 1, 'y751534936469_khach_san_grand_tourane63.jpg', 'Chưa có nội dung !', '2022-12-24 03:42:31', NULL),
(309, 11, '2', 2, '214.mp4', 'Chưa có nội dung !', '2022-12-24 03:44:25', NULL),
(310, 11, '139587411', 1, '13958741128.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(311, 11, '139590744', 1, '13959074454.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(312, 11, '139590752-1', 1, '139590752-124.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(313, 11, '139590793', 1, '13959079372.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(314, 11, '139591409', 1, '13959140946.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(315, 11, '139591411', 1, '13959141123.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(316, 11, '159472672', 1, '15947267264.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(317, 11, '159472678 (1)', 1, '159472678 (1)90.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(318, 11, '159472678', 1, '15947267824.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(319, 11, '226582810', 1, '22658281058.jpg', 'Chưa có nội dung !', '2022-12-24 03:44:42', NULL),
(320, 10, '0', 2, '020.mp4', 'Chưa có nội dung !', '2022-12-24 03:45:48', NULL),
(321, 10, 'c20a9590', 1, 'c20a959031.jfif', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(322, 10, 'chi07885', 1, 'chi0788583.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(323, 10, 'chi07917-edit', 1, 'chi07917-edit59.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(324, 10, 'chi07967-edit', 1, 'chi07967-edit80.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(325, 10, 'chi08105-edit', 1, 'chi08105-edit16.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(326, 10, 'chi08155-edit', 1, 'chi08155-edit23.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(327, 10, 'edhuQe02TVeWipcX8I9W1w-296', 1, 'edhuQe02TVeWipcX8I9W1w-2967.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(328, 10, 'jfMvp-RiTXqg3zoAqwsOmw-302', 1, 'jfMvp-RiTXqg3zoAqwsOmw-30229.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(329, 10, 'k_AXtJzJQQOzb-SECGNXiA-288', 1, 'k_AXtJzJQQOzb-SECGNXiA-28826.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(330, 10, 'KsTI9yQlRpifWwgEeiTn7A-0', 1, 'KsTI9yQlRpifWwgEeiTn7A-050.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(331, 10, 'suite-resize', 1, 'suite-resize13.png', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(332, 10, 'SVoDajCBSZmO4UvOc9ISLg-2', 1, 'SVoDajCBSZmO4UvOc9ISLg-290.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(333, 10, 'wdo1500478859_khach_san_mandila_beach_da_nang', 1, 'wdo1500478859_khach_san_mandila_beach_da_nang70.jpg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(334, 10, 'zwX5WYt8QT2MysTEGqHVZg-0', 1, 'zwX5WYt8QT2MysTEGqHVZg-087.jpeg', 'Chưa có nội dung !', '2022-12-24 03:46:10', NULL),
(335, 7, 'chi07885', 1, 'chi0788599.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(336, 7, 'chi07917-edit', 1, 'chi07917-edit84.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(337, 7, 'chi07967-edit', 1, 'chi07967-edit18.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(338, 7, 'chi08105-edit', 1, 'chi08105-edit97.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(339, 7, 'chi08155-edit', 1, 'chi08155-edit41.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(340, 7, 'edhuQe02TVeWipcX8I9W1w-296', 1, 'edhuQe02TVeWipcX8I9W1w-29626.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(341, 7, 'jfMvp-RiTXqg3zoAqwsOmw-302', 1, 'jfMvp-RiTXqg3zoAqwsOmw-30219.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(342, 7, 'k_AXtJzJQQOzb-SECGNXiA-288', 1, 'k_AXtJzJQQOzb-SECGNXiA-28857.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(343, 7, 'KsTI9yQlRpifWwgEeiTn7A-0', 1, 'KsTI9yQlRpifWwgEeiTn7A-037.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(344, 7, 'suite-resize', 1, 'suite-resize25.png', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(345, 7, 'SVoDajCBSZmO4UvOc9ISLg-2', 1, 'SVoDajCBSZmO4UvOc9ISLg-215.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(346, 7, 'wdo1500478859_khach_san_mandila_beach_da_nang', 1, 'wdo1500478859_khach_san_mandila_beach_da_nang81.jpg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(347, 7, 'zwX5WYt8QT2MysTEGqHVZg-0', 1, 'zwX5WYt8QT2MysTEGqHVZg-053.jpeg', 'Chưa có nội dung !', '2022-12-24 03:47:22', NULL),
(348, 7, '0', 2, '020.mp4', 'Chưa có nội dung !', '2022-12-24 03:47:32', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_gallery_restaurant`
--

CREATE TABLE `tbl_gallery_restaurant` (
  `gallery_restaurant_id` int(11) NOT NULL,
  `restaurant_id` int(11) DEFAULT NULL,
  `gallery_restaurant_name` varchar(255) NOT NULL,
  `gallery_restaurant_image` varchar(255) NOT NULL,
  `gallery_restaurant_content` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_gallery_restaurant`
--

INSERT INTO `tbl_gallery_restaurant` (`gallery_restaurant_id`, `restaurant_id`, `gallery_restaurant_name`, `gallery_restaurant_image`, `gallery_restaurant_content`, `created_at`, `updated_at`) VALUES
(4, 1, '33360729036316693870531965559916984775079003n-9633', '33360729036316693870531965559916984775079003n-963338.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:07:49', '2024-10-15 17:07:49'),
(5, 1, '33494935610193821825472191278423870453619842n-5743', '33494935610193821825472191278423870453619842n-574332.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:08:42', '2024-10-15 17:08:42'),
(6, 1, '3349505787385489513136353647203604490792204n-1387', '3349505787385489513136353647203604490792204n-138717.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:08:42', '2024-10-15 17:08:42'),
(7, 1, '3711242912678660261596242252007157801576040n-6246', '3711242912678660261596242252007157801576040n-624689.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:08:42', '2024-10-15 17:08:42'),
(8, 1, '4346740684003440362451557391267983005745702n-7273', '4346740684003440362451557391267983005745702n-727352.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:22:29', '2024-10-15 17:22:29'),
(9, 1, 'img077a-9898', 'img077a-989861.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:22:29', '2024-10-15 17:22:29'),
(10, 1, 'z52987754353988316088990a8b19a3a6bc4951a683c52-7472', 'z52987754353988316088990a8b19a3a6bc4951a683c52-747225.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:22:29', '2024-10-15 17:22:29'),
(11, 4, '2024-05-21', '2024-05-2160.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(12, 4, '449827642_122155174514222726_6412376102903227455_n', '449827642_122155174514222726_6412376102903227455_n62.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(13, 4, 'caption', 'caption96.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(14, 4, 'img077a-9898', 'img077a-989819.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(15, 4, 'thia-go-restaurant-da-nang', 'thia-go-restaurant-da-nang58.png', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(16, 4, 'z52987754353988316088990a8b19a3a6bc4951a683c52-7472', 'z52987754353988316088990a8b19a3a6bc4951a683c52-747292.jpg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:41:33', '2024-10-15 17:41:33'),
(17, 5, 'Screenshot_16-10-2024_0459_cabanonpalace', 'Screenshot_16-10-2024_0459_cabanonpalace35.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:55:18', '2024-10-15 17:55:18'),
(18, 5, 'Screenshot_16-10-2024_0464_cabanonpalace', 'Screenshot_16-10-2024_0464_cabanonpalace69.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:55:18', '2024-10-15 17:55:18'),
(19, 5, 'Screenshot_16-10-2024_04534_cabanonpalace', 'Screenshot_16-10-2024_04534_cabanonpalace46.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:55:18', '2024-10-15 17:55:18'),
(20, 5, 'Screenshot_16-10-2024_04547_cabanonpalace', 'Screenshot_16-10-2024_04547_cabanonpalace56.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:55:18', '2024-10-15 17:55:18'),
(21, 5, 'Screenshot_16-10-2024_04615_cabanonpalace', 'Screenshot_16-10-2024_04615_cabanonpalace29.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-15 17:55:18', '2024-10-15 17:55:18'),
(22, 6, 'home-tmk-banner', 'home-tmk-banner88.png', 'Ảnh này chưa có nội dung !', '2024-10-16 14:06:12', '2024-10-16 14:06:12'),
(23, 6, '279111200_1947513572122955_454290677711266898_n', '279111200_1947513572122955_454290677711266898_n87.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:07:40', '2024-10-16 14:07:40'),
(24, 6, 'OIP', 'OIP70.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:08:00', '2024-10-16 14:08:00'),
(25, 6, 'R', 'R98.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:08:00', '2024-10-16 14:08:00'),
(26, 7, '279111200_1947513572122955_454290677711266898_n', '279111200_1947513572122955_454290677711266898_n23.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:18:19', '2024-10-16 14:18:19'),
(27, 7, '463283449_122186356832085079_5135685110275125858_n', '463283449_122186356832085079_5135685110275125858_n40.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:18:19', '2024-10-16 14:18:19'),
(28, 7, '463597371_122186356826085079_6792514180605106207_n', '463597371_122186356826085079_6792514180605106207_n15.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:18:19', '2024-10-16 14:18:19'),
(29, 7, 'Screenshot_16-10-2024_211315_docs', 'Screenshot_16-10-2024_211315_docs4.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:18:19', '2024-10-16 14:18:19'),
(30, 8, '222309-mdl-am-thuc-web', '222309-mdl-am-thuc-web1.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(31, 8, '222309-mdl-con-nguoi-2-web', '222309-mdl-con-nguoi-2-web51.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(32, 8, '222309-mdl-khong-gian-web', '222309-mdl-khong-gian-web17.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(33, 8, '3349505787385489513136353647203604490792204n-1387', '3349505787385489513136353647203604490792204n-13878.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(34, 8, 'itgFCtWs7qxMu3guIelui24byjILxYIh', 'itgFCtWs7qxMu3guIelui24byjILxYIh48.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(35, 8, 'Screenshot_16-10-2024_213833_docs', 'Screenshot_16-10-2024_213833_docs53.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-16 14:53:16', '2024-10-16 14:53:16'),
(36, 9, '2f45eefa-2d1a-4721-91c3-ed3dd6fec6b0', '2f45eefa-2d1a-4721-91c3-ed3dd6fec6b098.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 15:11:27', '2024-10-16 15:11:27'),
(37, 9, '8ba7b422-f0c5-46be-ae90-86744436aa2b', '8ba7b422-f0c5-46be-ae90-86744436aa2b84.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 15:11:27', '2024-10-16 15:11:27'),
(38, 9, '364b52d9-0659-4744-b796-e0c29a038e43', '364b52d9-0659-4744-b796-e0c29a038e4386.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 15:11:27', '2024-10-16 15:11:27'),
(39, 9, 'rhCErsjS5hsz6Ah5MB1Q0cBeB80EggIG', 'rhCErsjS5hsz6Ah5MB1Q0cBeB80EggIG21.jpg', 'Ảnh này chưa có nội dung !', '2024-10-16 15:11:27', '2024-10-16 15:11:27'),
(40, 9, 'Screenshot_16-10-2024_215531_docs', 'Screenshot_16-10-2024_215531_docs97.jpeg', 'Ảnh này chưa có nội dung !', '2024-10-16 15:11:27', '2024-10-16 15:11:27');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_gallery_room`
--

CREATE TABLE `tbl_gallery_room` (
  `gallery_room_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `gallery_room_name` varchar(256) NOT NULL,
  `gallery_room_image` varchar(256) NOT NULL,
  `gallery_room_content` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_gallery_room`
--

INSERT INTO `tbl_gallery_room` (`gallery_room_id`, `room_id`, `gallery_room_name`, `gallery_room_image`, `gallery_room_content`, `created_at`, `deleted_at`) VALUES
(20, 2, '45623_8232G1LMQV_GRAND-SUITE-(3)', '45623_8232G1LMQV_GRAND-SUITE-(3)8.jpg', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(21, 2, '45623_VISFP2PBM1_GRAND-SUITE-(2)', '45623_VISFP2PBM1_GRAND-SUITE-(2)54.jpg', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(22, 2, '45623_YGMOPRD9SF_GRAND-SUITE-(4)', '45623_YGMOPRD9SF_GRAND-SUITE-(4)33.jpg', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(23, 2, 'photos_BA2DC9R8V5__tmp_playtemp8065542705427177172_multipartBody8263703920278520742asTemporaryFile', 'photos_BA2DC9R8V5__tmp_playtemp8065542705427177172_multipartBody8263703920278520742asTemporaryFile77.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(24, 2, 'photos_V225UTDXAL__tmp_playtemp8065542705427177172_multipartBody2090914398915981361asTemporaryFile', 'photos_V225UTDXAL__tmp_playtemp8065542705427177172_multipartBody2090914398915981361asTemporaryFile98.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(25, 2, 'photos_VFBCE6OVD9__tmp_playtemp8065542705427177172_multipartBody5015695692864059316asTemporaryFile', 'photos_VFBCE6OVD9__tmp_playtemp8065542705427177172_multipartBody5015695692864059316asTemporaryFile25.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:33', NULL),
(26, 3, 'photos_2GZ4AKXHXP__tmp_playtemp8065542705427177172_multipartBody6124056577060166012asTemporaryFile', 'photos_2GZ4AKXHXP__tmp_playtemp8065542705427177172_multipartBody6124056577060166012asTemporaryFile24.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(27, 3, 'photos_5U8KDRWWXJ__tmp_playtemp8065542705427177172_multipartBody5497779024820296510asTemporaryFile', 'photos_5U8KDRWWXJ__tmp_playtemp8065542705427177172_multipartBody5497779024820296510asTemporaryFile53.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(28, 3, 'photos_6KC43QSMVF__tmp_playtemp8065542705427177172_multipartBody7432058694583193243asTemporaryFile', 'photos_6KC43QSMVF__tmp_playtemp8065542705427177172_multipartBody7432058694583193243asTemporaryFile52.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(29, 3, 'photos_14HY44JHFI__tmp_playtemp8065542705427177172_multipartBody5756730443587435410asTemporaryFile', 'photos_14HY44JHFI__tmp_playtemp8065542705427177172_multipartBody5756730443587435410asTemporaryFile38.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(30, 3, 'photos_NJM9X62O52__tmp_playtemp8065542705427177172_multipartBody9169668318502362069asTemporaryFile', 'photos_NJM9X62O52__tmp_playtemp8065542705427177172_multipartBody9169668318502362069asTemporaryFile9.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(31, 3, 'photos_ON41JCB2AZ__tmp_playtemp8065542705427177172_multipartBody7110161233802501672asTemporaryFile', 'photos_ON41JCB2AZ__tmp_playtemp8065542705427177172_multipartBody7110161233802501672asTemporaryFile72.jfif', 'Chưa có nội dung !', '2022-11-09 16:19:47', NULL),
(32, 5, 'photos_BBIZMARRH1__tmp_playtemp8065542705427177172_multipartBody9156370589746065793asTemporaryFile', 'photos_BBIZMARRH1__tmp_playtemp8065542705427177172_multipartBody9156370589746065793asTemporaryFile34.jfif', 'Chưa có nội dung !', '2022-11-09 16:20:09', NULL),
(33, 5, 'photos_JTDVBKCE6K__tmp_playtemp8065542705427177172_multipartBody681062406435386945asTemporaryFile', 'photos_JTDVBKCE6K__tmp_playtemp8065542705427177172_multipartBody681062406435386945asTemporaryFile2.jfif', 'Chưa có nội dung !', '2022-11-09 16:20:09', NULL),
(34, 5, 'photos_N7IT26U82G__tmp_playtemp8065542705427177172_multipartBody4693596516512091483asTemporaryFile', 'photos_N7IT26U82G__tmp_playtemp8065542705427177172_multipartBody4693596516512091483asTemporaryFile12.jfif', 'Chưa có nội dung !', '2022-11-09 16:20:09', NULL),
(35, 5, 'photos_TW6EZAXSPR__tmp_playtemp8065542705427177172_multipartBody8620729709292563780asTemporaryFile', 'photos_TW6EZAXSPR__tmp_playtemp8065542705427177172_multipartBody8620729709292563780asTemporaryFile73.jfif', 'Chưa có nội dung !', '2022-11-09 16:20:09', NULL),
(36, 5, 'photos_X675X92ZFM__tmp_playtemp8065542705427177172_multipartBody8452613549746471179asTemporaryFile', 'photos_X675X92ZFM__tmp_playtemp8065542705427177172_multipartBody8452613549746471179asTemporaryFile82.jfif', 'Chưa có nội dung !', '2022-11-09 16:20:09', NULL),
(37, 18, 'deluxe-room-1', 'deluxe-room-164.jpg', 'Chưa có nội dung !', '2022-12-23 08:46:41', NULL),
(38, 18, 'deluxe-room-6', 'deluxe-room-66.jpg', 'Chưa có nội dung !', '2022-12-23 08:46:41', NULL),
(39, 18, 'deluxe-room-7', 'deluxe-room-773.jpg', 'Chưa có nội dung !', '2022-12-23 08:46:41', NULL),
(40, 18, 'deluxe-room-8', 'deluxe-room-855.jpg', 'Chưa có nội dung !', '2022-12-23 08:46:41', NULL),
(41, 19, 'deluxe-room---city-view-1', 'deluxe-room---city-view-154.jpg', 'Chưa có nội dung !', '2022-12-23 08:47:51', NULL),
(42, 19, 'deluxe-room---city-view-4', 'deluxe-room---city-view-453.jpg', 'Chưa có nội dung !', '2022-12-23 08:47:51', NULL),
(43, 19, 'deluxe-room---city-view-5', 'deluxe-room---city-view-546.jpg', 'Chưa có nội dung !', '2022-12-23 08:47:51', NULL),
(44, 19, 'deluxe-room---city-view-6', 'deluxe-room---city-view-665.jpg', 'Chưa có nội dung !', '2022-12-23 08:47:51', NULL),
(45, 20, '1', '164.jpg', 'Chưa có nội dung !', '2022-12-23 08:48:49', NULL),
(46, 20, '2', '214.jpg', 'Chưa có nội dung !', '2022-12-23 08:48:49', NULL),
(47, 20, '3', '321.jpg', 'Chưa có nội dung !', '2022-12-23 08:48:49', NULL),
(48, 20, '7', '795.jpg', 'Chưa có nội dung !', '2022-12-23 08:48:49', NULL),
(49, 15, '23187c1fc04dcfbc05bb4ae341d39f65', '23187c1fc04dcfbc05bb4ae341d39f6519.jpg', 'Chưa có nội dung !', '2022-12-23 08:53:49', NULL),
(50, 15, 'dcf59f78858774fc80d3b7a67592d0e4', 'dcf59f78858774fc80d3b7a67592d0e417.jpg', 'Chưa có nội dung !', '2022-12-23 08:53:49', NULL),
(51, 15, 'dsc00808-edit', 'dsc00808-edit32.jpg', 'Chưa có nội dung !', '2022-12-23 08:53:49', NULL),
(52, 15, 'grand-touruer-10', 'grand-touruer-1059.jpg', 'Chưa có nội dung !', '2022-12-23 08:53:49', NULL),
(53, 16, '23187c1fc04dcfbc05bb4ae341d39f65', '23187c1fc04dcfbc05bb4ae341d39f6599.jpg', 'Chưa có nội dung !', '2022-12-23 08:54:37', NULL),
(54, 16, 'dcf59f78858774fc80d3b7a67592d0e4', 'dcf59f78858774fc80d3b7a67592d0e44.jpg', 'Chưa có nội dung !', '2022-12-23 08:54:37', NULL),
(55, 16, 'dsc09935-edit-copy', 'dsc09935-edit-copy37.jpg', 'Chưa có nội dung !', '2022-12-23 08:54:37', NULL),
(56, 16, 'grand-tourane-noi-that-3', 'grand-tourane-noi-that-349.jpg', 'Chưa có nội dung !', '2022-12-23 08:54:37', NULL),
(57, 17, 'dsc09910-edit-edit', 'dsc09910-edit-edit97.jpg', 'Chưa có nội dung !', '2022-12-23 08:55:39', NULL),
(58, 17, 'grand-touruer-10', 'grand-touruer-1041.jpg', 'Chưa có nội dung !', '2022-12-23 08:55:39', NULL),
(59, 17, 'Xe65baeRRS2cDlL8LjmrZw-72', 'Xe65baeRRS2cDlL8LjmrZw-7294.jpeg', 'Chưa có nội dung !', '2022-12-23 08:55:39', NULL),
(60, 17, 'Xe65baeRRS2cDlL8LjmrZw-73', 'Xe65baeRRS2cDlL8LjmrZw-7312.jpeg', 'Chưa có nội dung !', '2022-12-23 08:55:39', NULL),
(61, 21, '1', '143.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:44', NULL),
(62, 21, '2', '262.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:44', NULL),
(63, 21, '4', '444.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:44', NULL),
(64, 21, '5', '511.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:44', NULL),
(65, 22, '2', '277.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:54', NULL),
(66, 22, '3', '312.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:54', NULL),
(67, 22, '4', '434.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:54', NULL),
(68, 22, '5 (1)', '5 (1)32.jpg', 'Chưa có nội dung !', '2022-12-23 09:06:54', NULL),
(69, 23, '2', '258.jpg', 'Chưa có nội dung !', '2022-12-23 09:07:05', NULL),
(70, 23, '3', '362.jpg', 'Chưa có nội dung !', '2022-12-23 09:07:05', NULL),
(71, 23, '4 (1)', '4 (1)56.jpg', 'Chưa có nội dung !', '2022-12-23 09:07:05', NULL),
(72, 23, '5', '510.jpg', 'Chưa có nội dung !', '2022-12-23 09:07:05', NULL),
(73, 10, '422_E5M56T4Q2D_194940667', '422_E5M56T4Q2D_19494066773.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:14', NULL),
(74, 10, '422_TCCGDWNNVR_110318274', '422_TCCGDWNNVR_11031827456.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:14', NULL),
(75, 10, 'hyatt-regency-danang-resort-and-spa-p383-standard-garden-king-guestroom', 'hyatt-regency-danang-resort-and-spa-p383-standard-garden-king-guestroom20.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:14', NULL),
(76, 10, 'hyatt-regency-danang-resort-and-spa-p384-standard-garden-twin-guestroom', 'hyatt-regency-danang-resort-and-spa-p384-standard-garden-twin-guestroom90.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:14', NULL),
(77, 9, '4ea2f591_z', '4ea2f591_z34.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:52', NULL),
(78, 9, '22bf9578_z', '22bf9578_z27.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:52', NULL),
(79, 9, '98a23f13_z', '98a23f13_z50.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:52', NULL),
(80, 9, '5461e712_z', '5461e712_z72.jpg', 'Chưa có nội dung !', '2022-12-23 09:13:52', NULL),
(81, 11, '23ddc28f7f0a0951d672263a796b9a7c', '23ddc28f7f0a0951d672263a796b9a7c90.jpg', 'Chưa có nội dung !', '2022-12-23 09:14:36', NULL),
(82, 11, '422_AOEKK37A4I_114417617', '422_AOEKK37A4I_11441761717.jpg', 'Chưa có nội dung !', '2022-12-23 09:14:36', NULL),
(83, 11, '230260870', '23026087075.jpg', 'Chưa có nội dung !', '2022-12-23 09:14:36', NULL),
(84, 11, 'photos_TQBWKVNSFS__tmp_playtemp9150386112140494575_multipartBody4274278420470169316asTemporaryFile', 'photos_TQBWKVNSFS__tmp_playtemp9150386112140494575_multipartBody4274278420470169316asTemporaryFile12.jfif', 'Chưa có nội dung !', '2022-12-23 09:14:36', NULL),
(85, 6, '1', '196.jpg', 'Chưa có nội dung !', '2022-12-23 09:17:29', NULL),
(86, 6, '2', '294.jpg', 'Chưa có nội dung !', '2022-12-23 09:17:29', NULL),
(87, 6, '3', '346.jpg', 'Chưa có nội dung !', '2022-12-23 09:17:29', NULL),
(88, 6, '5', '569.jpg', 'Chưa có nội dung !', '2022-12-23 09:17:29', NULL),
(89, 7, '2', '268.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:04', NULL),
(90, 7, '3', '333.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:04', NULL),
(91, 7, '4', '430.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:04', NULL),
(92, 7, '5 (1)', '5 (1)29.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:04', NULL),
(93, 8, '1', '15.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:43', NULL),
(94, 8, '35180_5DDFT09LMR_VPCRFDN_Lobby11', '35180_5DDFT09LMR_VPCRFDN_Lobby1191.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:43', NULL),
(95, 8, '35180_LKLH41D98X_VPCRFDN_Facade13', '35180_LKLH41D98X_VPCRFDN_Facade1327.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:43', NULL),
(96, 8, '35180_N74NGRIXJW_VPCRFDN_Executive Suite River View Room5', '35180_N74NGRIXJW_VPCRFDN_Executive Suite River View Room540.jpg', 'Chưa có nội dung !', '2022-12-23 09:18:43', NULL),
(97, 24, 'deluxe---king-13', 'deluxe---king-1386.jpg', 'Chưa có nội dung !', '2022-12-23 09:26:48', NULL),
(98, 24, 'deluxe---king-23', 'deluxe---king-2361.jpg', 'Chưa có nội dung !', '2022-12-23 09:26:48', NULL),
(99, 24, 'deluxe---king-33', 'deluxe---king-3358.jpg', 'Chưa có nội dung !', '2022-12-23 09:26:48', NULL),
(100, 24, 'deluxe---king-63', 'deluxe---king-6311.jpg', 'Chưa có nội dung !', '2022-12-23 09:26:48', NULL),
(101, 25, 'deluxe---twin-13', 'deluxe---twin-1371.jpg', 'Chưa có nội dung !', '2022-12-23 09:27:26', NULL),
(102, 25, 'deluxe---twin-23', 'deluxe---twin-2388.jpg', 'Chưa có nội dung !', '2022-12-23 09:27:26', NULL),
(103, 25, 'deluxe---twin-33', 'deluxe---twin-3367.jpg', 'Chưa có nội dung !', '2022-12-23 09:27:26', NULL),
(104, 25, 'deluxe---twin-63', 'deluxe---twin-6398.jpg', 'Chưa có nội dung !', '2022-12-23 09:27:26', NULL),
(105, 26, 'deluxe---king-63', 'deluxe---king-6314.jpg', 'Chưa có nội dung !', '2022-12-23 09:28:06', NULL),
(106, 26, 'premium-deluxe---king-13 (1)', 'premium-deluxe---king-13 (1)20.jpg', 'Chưa có nội dung !', '2022-12-23 09:28:06', NULL),
(107, 26, 'premium-deluxe---king-13', 'premium-deluxe---king-1349.jpg', 'Chưa có nội dung !', '2022-12-23 09:28:06', NULL),
(108, 26, 'premium-deluxe---king-23', 'premium-deluxe---king-2345.jpg', 'Chưa có nội dung !', '2022-12-23 09:28:06', NULL),
(109, 26, 'premium-deluxe---king-33', 'premium-deluxe---king-338.jpg', 'Chưa có nội dung !', '2022-12-23 09:28:06', NULL),
(110, 12, '_KgSKL9jQ8mm-myNc9ZVww-89', '_KgSKL9jQ8mm-myNc9ZVww-8965.jpeg', 'Chưa có nội dung !', '2022-12-23 18:13:52', NULL),
(111, 12, '170121072', '17012107269.jpg', 'Chưa có nội dung !', '2022-12-23 18:13:52', NULL),
(112, 12, '170121079', '17012107990.jpg', 'Chưa có nội dung !', '2022-12-23 18:13:52', NULL),
(113, 12, 'mxsMXp6KSciK6R2huKA7Uw-75', 'mxsMXp6KSciK6R2huKA7Uw-7517.jpeg', 'Chưa có nội dung !', '2022-12-23 18:13:52', NULL),
(114, 13, '170121048', '17012104864.jpg', 'Chưa có nội dung !', '2022-12-23 18:14:36', NULL),
(115, 13, '170121049', '17012104922.jpg', 'Chưa có nội dung !', '2022-12-23 18:14:36', NULL),
(116, 13, '170121049-1', '170121049-139.jpg', 'Chưa có nội dung !', '2022-12-23 18:14:36', NULL),
(117, 13, '170121185', '17012118582.jpg', 'Chưa có nội dung !', '2022-12-23 18:14:36', NULL),
(118, 14, '170121048', '17012104847.jpg', 'Chưa có nội dung !', '2022-12-23 18:15:27', NULL),
(119, 14, '170121049', '17012104920.jpg', 'Chưa có nội dung !', '2022-12-23 18:15:27', NULL),
(120, 14, '170121049-1', '170121049-166.jpg', 'Chưa có nội dung !', '2022-12-23 18:15:27', NULL),
(121, 14, '170121185', '17012118565.jpg', 'Chưa có nội dung !', '2022-12-23 18:15:27', NULL),
(122, 27, '3', '364.jpg', 'Chưa có nội dung !', '2022-12-23 18:26:23', NULL),
(123, 27, '4', '41.jpg', 'Chưa có nội dung !', '2022-12-23 18:26:23', NULL),
(124, 27, 'le-sands-ocean-deluxe-cameo-1', 'le-sands-ocean-deluxe-cameo-156.jpg', 'Chưa có nội dung !', '2022-12-23 18:26:23', NULL),
(125, 27, 'le-sands-ocean-deluxe-twin-1', 'le-sands-ocean-deluxe-twin-139.jpg', 'Chưa có nội dung !', '2022-12-23 18:26:23', NULL),
(126, 28, '1', '18.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:13', NULL),
(127, 28, '3', '389.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:13', NULL),
(128, 28, 'le-sands-ocean-deluxe-double-1', 'le-sands-ocean-deluxe-double-151.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:13', NULL),
(129, 28, 'le-sands-ocean-deluxe-double-2', 'le-sands-ocean-deluxe-double-213.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:13', NULL),
(130, 29, 'le-sands-ocean-deluxe-bathroom-1', 'le-sands-ocean-deluxe-bathroom-182.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:50', NULL),
(131, 29, 'le-sands-ocean-deluxe-cameo-2', 'le-sands-ocean-deluxe-cameo-22.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:50', NULL),
(132, 29, 'le-sands-ocean-deluxe-twin-1', 'le-sands-ocean-deluxe-twin-153.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:50', NULL),
(133, 29, 'le-sands-ocean-deluxe-twin-2', 'le-sands-ocean-deluxe-twin-293.jpg', 'Chưa có nội dung !', '2022-12-23 18:27:50', NULL),
(134, 30, '3faa23b8', '3faa23b876.jpg', 'Chưa có nội dung !', '2022-12-23 18:36:31', NULL),
(135, 30, '2486094_18011815450061166003', '2486094_1801181545006116600339.jpg', 'Chưa có nội dung !', '2022-12-23 18:36:31', NULL),
(136, 30, '125834586', '12583458630.jpg', 'Chưa có nội dung !', '2022-12-23 18:36:31', NULL),
(137, 30, 'db8dd21b', 'db8dd21b14.jpg', 'Chưa có nội dung !', '2022-12-23 18:36:31', NULL),
(138, 31, '0f13f82e', '0f13f82e28.jpg', 'Chưa có nội dung !', '2022-12-23 18:37:13', NULL),
(140, 31, 's4h1516094709_khach_san_dana_marina', 's4h1516094709_khach_san_dana_marina43.jpg', 'Chưa có nội dung !', '2022-12-23 18:37:13', NULL),
(141, 31, 'ssl1516094716_khach_san_dana_marina', 'ssl1516094716_khach_san_dana_marina34.jpg', 'Chưa có nội dung !', '2022-12-23 18:37:13', NULL),
(142, 31, 'ssl1516094716_khach_san_dana_marina', 'ssl1516094716_khach_san_dana_marina61.jpg', 'Chưa có nội dung !', '2022-12-23 18:38:03', NULL),
(143, 33, '1', '195.jpg', 'Chưa có nội dung !', '2022-12-23 18:47:20', NULL),
(144, 33, 'sup', 'sup74.jpg', 'Chưa có nội dung !', '2022-12-23 18:47:20', NULL),
(145, 33, 'sup1', 'sup114.jpg', 'Chưa có nội dung !', '2022-12-23 18:47:20', NULL),
(146, 33, 'z3853686043814_b471469f9a49a70fbb374d610b7a6ca0', 'z3853686043814_b471469f9a49a70fbb374d610b7a6ca066.jpg', 'Chưa có nội dung !', '2022-12-23 18:47:20', NULL),
(147, 34, '11', '1128.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:01', NULL),
(148, 34, '13', '1395.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:01', NULL),
(149, 34, '37d05a73', '37d05a732.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:01', NULL),
(150, 34, 'GwUzZzmZQ2qS_tN4sd4PtA-12', 'GwUzZzmZQ2qS_tN4sd4PtA-1287.jpeg', 'Chưa có nội dung !', '2022-12-23 18:48:01', NULL),
(151, 35, '1111', '11112.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:55', NULL),
(152, 35, '1112', '111260.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:55', NULL),
(153, 35, 'z3903433331955_a09c4b446c127bad1b7a2da0147b5d51', 'z3903433331955_a09c4b446c127bad1b7a2da0147b5d5147.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:55', NULL),
(154, 35, 'z3903433339520_35851348ee72b2a10d78bf69fb42d67d', 'z3903433339520_35851348ee72b2a10d78bf69fb42d67d28.jpg', 'Chưa có nội dung !', '2022-12-23 18:48:55', NULL),
(155, 36, '139590463', '1395904634.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:10', NULL),
(156, 36, '139591172', '13959117282.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:10', NULL),
(157, 36, '281652130', '28165213059.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:10', NULL),
(158, 36, '281652140', '28165214036.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:10', NULL),
(159, 37, '139587849', '13958784940.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:57', NULL),
(160, 37, '139589951', '13958995182.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:57', NULL),
(161, 37, '268417742', '26841774287.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:57', NULL),
(162, 37, '271340613', '27134061398.jpg', 'Chưa có nội dung !', '2022-12-23 18:56:57', NULL),
(163, 38, '139590752-1', '139590752-184.jpg', 'Chưa có nội dung !', '2022-12-23 18:57:50', NULL),
(164, 38, '139590782', '13959078237.jpg', 'Chưa có nội dung !', '2022-12-23 18:57:50', NULL),
(165, 38, '139590793', '13959079375.jpg', 'Chưa có nội dung !', '2022-12-23 18:57:50', NULL),
(166, 38, '226582810', '22658281092.jpg', 'Chưa có nội dung !', '2022-12-23 18:57:50', NULL),
(167, 39, '1', '161.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:10', NULL),
(169, 39, '5f27e9327b7eb923b35eee8bd81d0a08', '5f27e9327b7eb923b35eee8bd81d0a0836.png', 'Chưa có nội dung !', '2022-12-23 19:06:10', NULL),
(170, 39, '187025479', '18702547961.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:10', NULL),
(171, 40, '1', '174.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:48', NULL),
(172, 40, '3', '322.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:48', NULL),
(173, 40, '4', '47.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:48', NULL),
(174, 40, '6', '681.jpg', 'Chưa có nội dung !', '2022-12-23 19:06:48', NULL),
(175, 41, '9', '941.jpg', 'Chưa có nội dung !', '2022-12-23 19:07:41', NULL),
(176, 41, '10', '1025.jpg', 'Chưa có nội dung !', '2022-12-23 19:07:41', NULL),
(177, 41, '12', '1245.jpg', 'Chưa có nội dung !', '2022-12-23 19:07:41', NULL),
(178, 41, '13', '1339.jpg', 'Chưa có nội dung !', '2022-12-23 19:07:41', NULL),
(179, 32, '9', '926.jpg', 'Chưa có nội dung !', '2022-12-23 19:12:36', NULL),
(180, 32, '10', '1080.jpg', 'Chưa có nội dung !', '2022-12-23 19:12:36', NULL),
(181, 32, '12', '1283.jpg', 'Chưa có nội dung !', '2022-12-23 19:12:36', NULL),
(182, 32, '13', '130.jpg', 'Chưa có nội dung !', '2022-12-23 19:12:36', NULL),
(183, 42, '293df4e3e75c2c4abee7b51b07c25fd3', '293df4e3e75c2c4abee7b51b07c25fd35.jpg', 'Chưa có nội dung !', '2022-12-24 02:34:51', NULL),
(184, 42, 'photos_HXNVZN4C9Z__tmp_playtemp7458377284404767097_multipartBody1473705047806690222asTemporaryFile', 'photos_HXNVZN4C9Z__tmp_playtemp7458377284404767097_multipartBody1473705047806690222asTemporaryFile1.jfif', 'Chưa có nội dung !', '2022-12-24 02:34:51', NULL),
(185, 42, 'photos_PXB0QACP28__tmp_playtemp7458377284404767097_multipartBody3084394181656001311asTemporaryFile', 'photos_PXB0QACP28__tmp_playtemp7458377284404767097_multipartBody3084394181656001311asTemporaryFile90.jfif', 'Chưa có nội dung !', '2022-12-24 02:34:51', NULL),
(186, 43, 'b2e1b39b3939c51d41c121ad10d1f40d', 'b2e1b39b3939c51d41c121ad10d1f40d47.jpg', 'Chưa có nội dung !', '2022-12-24 02:35:31', NULL),
(187, 43, 'photos_8V76B67OHN__tmp_playtemp7458377284404767097_multipartBody7990948807478145368asTemporaryFile', 'photos_8V76B67OHN__tmp_playtemp7458377284404767097_multipartBody7990948807478145368asTemporaryFile71.jfif', 'Chưa có nội dung !', '2022-12-24 02:35:31', NULL),
(188, 43, 'photos_JITT86J8SB__tmp_playtemp7458377284404767097_multipartBody4685453065486123657asTemporaryFile', 'photos_JITT86J8SB__tmp_playtemp7458377284404767097_multipartBody4685453065486123657asTemporaryFile31.jfif', 'Chưa có nội dung !', '2022-12-24 02:35:31', NULL),
(189, 44, '293df4e3e75c2c4abee7b51b07c25fd3', '293df4e3e75c2c4abee7b51b07c25fd332.jpg', 'Chưa có nội dung !', '2022-12-24 02:36:16', NULL),
(190, 44, 'b2e1b39b3939c51d41c121ad10d1f40d', 'b2e1b39b3939c51d41c121ad10d1f40d46.jpg', 'Chưa có nội dung !', '2022-12-24 02:36:16', NULL),
(191, 44, 'photos_JITT86J8SB__tmp_playtemp7458377284404767097_multipartBody4685453065486123657asTemporaryFile', 'photos_JITT86J8SB__tmp_playtemp7458377284404767097_multipartBody4685453065486123657asTemporaryFile75.jfif', 'Chưa có nội dung !', '2022-12-24 02:36:16', NULL),
(192, 45, 'chi07547-edit', 'chi07547-edit74.jpg', 'Chưa có nội dung !', '2022-12-24 02:44:43', NULL),
(193, 45, 'deluxe-twin-resize', 'deluxe-twin-resize5.png', 'Chưa có nội dung !', '2022-12-24 02:44:43', NULL),
(194, 45, 'k_AXtJzJQQOzb-SECGNXiA-278', 'k_AXtJzJQQOzb-SECGNXiA-27895.jpeg', 'Chưa có nội dung !', '2022-12-24 02:44:43', NULL),
(195, 45, 'NTE-u9MwTFSn59nRar1k5w-514', 'NTE-u9MwTFSn59nRar1k5w-51491.jpeg', 'Chưa có nội dung !', '2022-12-24 02:44:43', NULL),
(196, 46, 'chi07528-edit', 'chi07528-edit22.jpg', 'Chưa có nội dung !', '2022-12-24 02:45:22', NULL),
(197, 46, 'chi07547-edit', 'chi07547-edit30.jpg', 'Chưa có nội dung !', '2022-12-24 02:45:22', NULL),
(198, 46, 'jfMvp-RiTXqg3zoAqwsOmw-295', 'jfMvp-RiTXqg3zoAqwsOmw-29538.jpeg', 'Chưa có nội dung !', '2022-12-24 02:45:22', NULL),
(199, 46, 'jfMvp-RiTXqg3zoAqwsOmw-296', 'jfMvp-RiTXqg3zoAqwsOmw-29669.jpeg', 'Chưa có nội dung !', '2022-12-24 02:45:22', NULL),
(200, 47, '8bot_rgdRga4Dv1zVW1CHg-0', '8bot_rgdRga4Dv1zVW1CHg-076.jpeg', 'Chưa có nội dung !', '2022-12-24 02:46:04', NULL),
(201, 47, 'jfMvp-RiTXqg3zoAqwsOmw-297', 'jfMvp-RiTXqg3zoAqwsOmw-29779.jpeg', 'Chưa có nội dung !', '2022-12-24 02:46:04', NULL),
(202, 47, 'k_AXtJzJQQOzb-SECGNXiA-280', 'k_AXtJzJQQOzb-SECGNXiA-28049.jpeg', 'Chưa có nội dung !', '2022-12-24 02:46:04', NULL),
(203, 47, 'partial-king-resize', 'partial-king-resize54.png', 'Chưa có nội dung !', '2022-12-24 02:46:04', NULL),
(204, 48, '29403_5PK588DRAP_1-', '29403_5PK588DRAP_1-57.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:20', NULL),
(205, 48, '29403_35AR53UY5W_28', '29403_35AR53UY5W_283.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:20', NULL),
(206, 48, 'photos_B5G1ES80BN__tmp_playtemp7458377284404767097_multipartBody5944432618838289494asTemporaryFile', 'photos_B5G1ES80BN__tmp_playtemp7458377284404767097_multipartBody5944432618838289494asTemporaryFile34.jfif', 'Chưa có nội dung !', '2022-12-24 02:53:20', NULL),
(207, 48, 'photos_U1D4Q1KCEP__tmp_playtemp7458377284404767097_multipartBody1981676071139028276asTemporaryFile', 'photos_U1D4Q1KCEP__tmp_playtemp7458377284404767097_multipartBody1981676071139028276asTemporaryFile24.jfif', 'Chưa có nội dung !', '2022-12-24 02:53:20', NULL),
(208, 49, '1', '181.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:58', NULL),
(209, 49, '2', '269.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:58', NULL),
(210, 49, '3', '323.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:58', NULL),
(211, 49, '29403_35AR53UY5W_28', '29403_35AR53UY5W_2840.jpg', 'Chưa có nội dung !', '2022-12-24 02:53:59', NULL),
(212, 50, '2', '277.jpg', 'Chưa có nội dung !', '2022-12-24 02:54:40', NULL),
(213, 50, '3', '370.jpg', 'Chưa có nội dung !', '2022-12-24 02:54:40', NULL),
(214, 50, 'photos_LMMDUY38TN__tmp_playtemp7458377284404767097_multipartBody216551872425421854asTemporaryFile', 'photos_LMMDUY38TN__tmp_playtemp7458377284404767097_multipartBody216551872425421854asTemporaryFile8.jfif', 'Chưa có nội dung !', '2022-12-24 02:54:40', NULL),
(215, 50, 'photos_VR3T0X5EXI__tmp_playtemp7458377284404767097_multipartBody2839818511034061530asTemporaryFile', 'photos_VR3T0X5EXI__tmp_playtemp7458377284404767097_multipartBody2839818511034061530asTemporaryFile86.jfif', 'Chưa có nội dung !', '2022-12-24 02:54:40', NULL),
(216, 51, '_dhp2896-copy-2', '_dhp2896-copy-287.jpg', 'Chưa có nội dung !', '2022-12-24 03:01:32', NULL),
(217, 51, '_dhp2954-copy', '_dhp2954-copy43.jpg', 'Chưa có nội dung !', '2022-12-24 03:01:32', NULL),
(218, 51, '_dhp2962-edit-copy', '_dhp2962-edit-copy53.jpg', 'Chưa có nội dung !', '2022-12-24 03:01:32', NULL),
(219, 51, 'cici', 'cici72.jpg', 'Chưa có nội dung !', '2022-12-24 03:01:32', NULL),
(220, 52, '_dhp2775-copy', '_dhp2775-copy85.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:07', NULL),
(221, 52, '_dhp2784-copy', '_dhp2784-copy93.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:07', NULL),
(222, 52, '_dhp2798-a', '_dhp2798-a59.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:07', NULL),
(223, 52, '_dhp2868-a', '_dhp2868-a14.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:07', NULL),
(224, 53, '1', '13.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:44', NULL),
(225, 53, '2fc60fc7', '2fc60fc779.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:44', NULL),
(226, 53, '801---1', '801---146.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:44', NULL),
(227, 53, 'afaf43a5', 'afaf43a511.jpg', 'Chưa có nội dung !', '2022-12-24 03:02:44', NULL),
(228, 54, '202', '20214.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:09', NULL),
(229, 54, 'img_1717', 'img_171748.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:09', NULL),
(230, 54, 'img_1719', 'img_171953.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:09', NULL),
(231, 54, 'img_1730', 'img_173084.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:09', NULL),
(232, 55, '3', '355.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:43', NULL),
(233, 55, '4', '489.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:43', NULL),
(234, 55, '9', '93.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:43', NULL),
(235, 55, '10', '1096.jpg', 'Chưa có nội dung !', '2022-12-24 03:11:43', NULL),
(236, 56, '210-dulxe-king-street', '210-dulxe-king-street72.jpg', 'Chưa có nội dung !', '2022-12-24 03:12:15', NULL),
(237, 56, '210-dulxe-king-street-1', '210-dulxe-king-street-130.jpg', 'Chưa có nội dung !', '2022-12-24 03:12:15', NULL),
(238, 56, '210-dulxe-king-street-2', '210-dulxe-king-street-279.jpg', 'Chưa có nội dung !', '2022-12-24 03:12:15', NULL),
(239, 56, '210-dulxe-king-street-4', '210-dulxe-king-street-490.jpg', 'Chưa có nội dung !', '2022-12-24 03:12:15', NULL),
(240, 57, 'be2efb85c8dbfc6fdb305fcd0ab37160', 'be2efb85c8dbfc6fdb305fcd0ab3716093.jpg', 'Chưa có nội dung !', '2022-12-24 03:20:47', NULL),
(241, 57, 'classic-1', 'classic-197.jpg', 'Chưa có nội dung !', '2022-12-24 03:20:47', NULL),
(242, 57, 'classic-3', 'classic-366.jpg', 'Chưa có nội dung !', '2022-12-24 03:20:47', NULL),
(243, 57, 'classic-4', 'classic-470.jpg', 'Chưa có nội dung !', '2022-12-24 03:20:47', NULL),
(244, 58, 'deluxe-twin-1', 'deluxe-twin-112.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:22', NULL),
(245, 58, 'deluxe-twin-2', 'deluxe-twin-232.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:22', NULL),
(246, 58, 'deluxe-twin-3', 'deluxe-twin-352.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:22', NULL),
(247, 58, 'deluxe-twin-4', 'deluxe-twin-413.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:22', NULL),
(248, 59, 'premium-1234', 'premium-123463.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:59', NULL),
(249, 59, 'sea-side-twin', 'sea-side-twin44.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:59', NULL),
(250, 59, 'sea-side-twin-2', 'sea-side-twin-262.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:59', NULL),
(251, 59, 'toilet', 'toilet43.jpg', 'Chưa có nội dung !', '2022-12-24 03:21:59', NULL),
(252, 60, 'photos_3BQOIXLBO8__tmp_playtemp6771664243652320621_multipartBody7654549941202300293asTemporaryFile', 'photos_3BQOIXLBO8__tmp_playtemp6771664243652320621_multipartBody7654549941202300293asTemporaryFile22.jfif', 'Chưa có nội dung !', '2022-12-24 03:28:43', NULL),
(253, 60, 'photos_IOR2ABIH3H__tmp_playtemp6771664243652320621_multipartBody3760648411063274895asTemporaryFile', 'photos_IOR2ABIH3H__tmp_playtemp6771664243652320621_multipartBody3760648411063274895asTemporaryFile57.jfif', 'Chưa có nội dung !', '2022-12-24 03:28:43', NULL),
(254, 60, 'photos_K76OA0LKSM__tmp_playtemp6771664243652320621_multipartBody5061915830082727062asTemporaryFile', 'photos_K76OA0LKSM__tmp_playtemp6771664243652320621_multipartBody5061915830082727062asTemporaryFile34.jfif', 'Chưa có nội dung !', '2022-12-24 03:28:43', NULL),
(255, 60, 'superior-interior', 'superior-interior83.jpg', 'Chưa có nội dung !', '2022-12-24 03:28:43', NULL),
(256, 61, '2019', '201971.jpg', 'Chưa có nội dung !', '2022-12-24 03:29:22', NULL),
(257, 61, '2019', '201928.jpg', 'Chưa có nội dung !', '2022-12-24 03:29:22', NULL),
(258, 61, '2019', '201993.jpg', 'Chưa có nội dung !', '2022-12-24 03:29:22', NULL),
(259, 61, 'photos_GEFM42BNNN__tmp_playtemp6771664243652320621_multipartBody2070575775065890681asTemporaryFile', 'photos_GEFM42BNNN__tmp_playtemp6771664243652320621_multipartBody2070575775065890681asTemporaryFile6.jfif', 'Chưa có nội dung !', '2022-12-24 03:29:22', NULL),
(260, 62, 'superior-interior', 'superior-interior90.jpg', 'Chưa có nội dung !', '2022-12-24 03:30:04', NULL),
(261, 62, 'superior-twin-1', 'superior-twin-12.jpg', 'Chưa có nội dung !', '2022-12-24 03:30:04', NULL),
(262, 62, 'superior-twin-2', 'superior-twin-225.jpg', 'Chưa có nội dung !', '2022-12-24 03:30:04', NULL),
(263, 62, 'superior-twin-3', 'superior-twin-361.jpg', 'Chưa có nội dung !', '2022-12-24 03:30:04', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_hotel`
--

CREATE TABLE `tbl_hotel` (
  `hotel_id` int(10) UNSIGNED NOT NULL,
  `hotel_name` varchar(255) NOT NULL,
  `hotel_rank` int(1) NOT NULL,
  `hotel_type` int(1) NOT NULL,
  `brand_id` int(11) NOT NULL,
  `area_id` int(11) NOT NULL,
  `hotel_placedetails` varchar(256) NOT NULL,
  `hotel_linkplace` varchar(256) NOT NULL,
  `hotel_jfameplace` text NOT NULL,
  `hotel_image` varchar(256) NOT NULL,
  `hotel_price_average` int(11) DEFAULT NULL,
  `hotel_desc` varchar(1200) NOT NULL,
  `hotel_tag_keyword` varchar(256) NOT NULL,
  `hotel_view` int(50) NOT NULL DEFAULT 0,
  `hotel_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_hotel`
--

INSERT INTO `tbl_hotel` (`hotel_id`, `hotel_name`, `hotel_rank`, `hotel_type`, `brand_id`, `area_id`, `hotel_placedetails`, `hotel_linkplace`, `hotel_jfameplace`, `hotel_image`, `hotel_price_average`, `hotel_desc`, `hotel_tag_keyword`, `hotel_view`, `hotel_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(2, 'Meliá Vinpearl Riverfront', 5, 2, 3, 8, '341, Trần Hưng Đạo, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0709238,108.2287754', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.8972672079885!2d108.22710671468417!3d16.070819988879943!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142182ef14654ad%3A0x12b541ef197a770e!2zMzQxIMSQLiBUcuG6p24gSMawbmcgxJDhuqFvLCBBbiBI4bqjaSBC4bqvYywgU8ahbiBUcsOgLCDEkMOgIE7hurVuZyA1NTAwMDAsIFZp4buHdCBOYW0!5e0!3m2!1svi!2s!4v1671884682824!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'photos41.jfif', 1311127, 'Đà Nẵng từ lâu đã được biết đến là địa điểm du lịch nổi tiếng bậc nhất của Việt Nam. Nơi đây có có những người dân thân thiện, ẩm thực phong phú. Bên cạnh đó không thể không kể đến trải nghiệm nghỉ dưỡng đẳng cấp 5 sao chuyên nghiệp. Vinpearl Condotel Riverfront Đà Nẵng là 1 trong những khách sạn 5 sao được đông đảo du khách lựa chọn là điểm đến lý tưởng.', 'Khách Sạn Đà Nẵng , Khách Sạn Căn Hộ , Khách Sạn 5 Sao , Furama', 26, 1, '2022-10-31 15:25:53', '2024-11-03 15:48:43', NULL),
(3, 'Mường Thanh Luxury', 5, 1, 1, 7, ' 270 Võ Nguyên Giáp, Bắc Mỹ Phú, Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.0537175,108.2447887', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3919.18102971533!2d106.66985131462272!3d10.797442992307275!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x317529296adecd7d%3A0x8b457ab0f7a96429!2zMjYxQyBOZ3V54buFbiBWxINuIFRy4buXaSwgUGjGsOG7nW5nIDEwLCBQaMO6IE5odeG6rW4sIFRow6BuaCBwaOG7kSBI4buTIENow60gTWluaCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671886533294!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'logo_4_219090750.jpg', 1490564, 'Tập đoàn Mường Thanh sở hữu chuỗi khách sạn đẳng cấp 5 sao tại nhiều điểm du lịch nổi tiếng của Việt Nam. Đây là điểm đến lý tưởng cho một trải nghiệm nghỉ dưỡng tuyệt vời.  Hãy cùng chúng tôi khám phá dịch vụ của một khách sạn 5 sao thuộc chuỗi khách sạn nổi tiếng đó - Mường Thanh Luxury Đà Nẵng.', 'Mường Thanh Luxury Đà Nẵng , Khách Sạn Đà Nẵng , Khách Sạn 5 Sao , Khách Sạn Ở Ngủ Hành Sơn', 42, 1, '2022-10-31 16:10:05', '2024-11-03 15:48:43', NULL),
(4, 'Sheraton Grand Resort', 5, 3, 7, 7, '35, Trường Sa, Quận Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '15.9806685,108.2760168', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3835.6309412560363!2d108.2741414146829!3d15.980638088935654!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314210e4d62aa785%3A0xc4299b51ed1ecdb!2zMzUgVHLGsOG7nW5nIFNhLCBIb8OgIEjhuqNpLCBOZ8WpIEjDoG5oIFPGoW4sIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671886443477!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '25336767131.jfif', 1381737, 'Khu nghỉ dưỡng Sheraton Grand Danang Resort có chất lượng phục vụ tốt được du khách đánh giá cao. Đến với khách sạn du khách có thể thỏa thích tận hưởng khung cảnh đẹp cùng địa điểm du lịch hấp dẫn. Dưới đây chúng tôi xin nêu ra một vài nét nổi bật về dịch vụ khách sạn hiện đang cung cấp.', 'Sheraton Grand Danang Resort , Khách Sạn 5 Sao , Khách Sạn Đà Nẵng', 9, 1, '2022-10-31 16:14:20', '2024-11-03 15:48:43', NULL),
(5, 'The Nalod', 5, 1, 8, 8, '192, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0719468,108.244688', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.8725803045395!2d108.24246751468422!3d16.072100588879188!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421785e94b3369%3A0x246143110cfb08cd!2zMTkyIFbDtSBOZ3V5w6puIEdpw6FwLCBQaMaw4bubYyBN4bu5LCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671886664875!5m2!1svi!2s\" width=\"768\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'logo_4_219146764.jpg', 1274957, 'Khách sạn The Nalod Đà Nẵng một trong những địa điểm dừng chân đáng lưu tâm. Đến đây, du khách sẽ được trải nghiệm những dịch vụ chăm sóc tốt nhất. Dưới đây là những thông tin cập nhật mới nhất về khách sạn.', 'Khách sạn The Nalod Đà Nẵng , Khách Sạn Đà Nẵng , Khách Sạn 5 Sao , Khách Sạn Giá Rẻ', 11, 1, '2022-10-31 16:18:01', '2024-11-03 15:48:43', NULL),
(6, 'Khách sạn Grand Tourane', 5, 1, 4, 8, '252, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0617746,108.2459532', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.0637409996807!2d108.24367861442758!3d16.06218178888529!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421782774c398d%3A0x47f7157ebefa8dfd!2zMjUyIFbDtSBOZ3V5w6puIEdpw6FwLCBQaMaw4bubYyBN4bu5LCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671783741511!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'jun20---grand-tourane---edit-beach-20.jpg', 1523515, 'Mỗi sáng sớm được thức dậy trong tiếng sóng vỗ lao xao ngoài bờ biển, một cảm giác thú vị và bỏ lại đằng sau những xô bồ của cuộc sống. Bạn sẽ được tận hưởng nhiều dịch vụ tiện ích hiện đại thoải mái hơn cả ở nhà. Hãy đến với Khách Sạn Grand Tourane để bạn tận hưởng trải nghiệm này nhé! Vậy chúng ta cùng khám phá khách sạn này xem thế nào nhé!', 'Khách Sạn Đà Nẵng, Khách Sạn Giá Rẻ, Khách Sạn 5 Sao, Khách Sạn', 25, 1, '2022-12-23 08:25:26', '2024-11-03 15:48:43', NULL),
(7, 'Khách Sạn Radisson', 5, 1, 6, 3, '170, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0740563,108.2447484', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.8357314520135!2d108.24257151468422!3d16.074011888878008!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314217d00cf9d865%3A0xd905b4d0179104a2!2zMTcwIFbDtSBOZ3V5w6puIEdpw6FwLCBQaMaw4bubYyBN4bu5LCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671784649933!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'overview-264.jpg', 3520000, 'Khách Sạn Radisson Đà Nẵng là nơi cung cấp dịch vụ lưu  trú lý tưởng cho sự vui vẻ và thư giãn của Quý khách.\r\n\r\nKhách Sạn Radisson Đà Nẵng là một nơi nghỉ dưỡng đạt tiêu chuẩn với các dịch vụ tiện nghi như: wifi miễn phí, nước uống miễn phí,... đảm bảo mang đến cho khách hàng sự thoải mái nhất. Với thiết kế thanh lịch và gần gũi, sang trọng, tất cả phòng của khách hàng đều có trang bị tiện nghi chu đáo. Các trang bị tiêu chuẩn trong phòng bao gồm: tivi, điều hòa, phòng tắm riêng Ngoài ra, khách sạn còn có thể gợi ý cho bạn những hoạt động vui chơi giải trí bảo đảm bạn luôn thấy hứng thú trong suốt kỳ nghỉ.', 'Khách Sạn Đà Nẵng, Khách Sạn Giá Rẻ, Khách Sạn 5 Sao, Khách Sạn', 31, 1, '2022-12-23 08:41:06', '2024-11-03 15:48:43', NULL),
(8, 'Khách Sạn Greenery', 4, 2, 7, 8, '76, Hà Bổng, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0658684,108.2442025', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.9922455345704!2d108.24202731468412!3d16.065892188883037!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421783db8441bf%3A0x18ad9c2b70cbf84f!2zNzYgSMOgIELhu5VuZywgUGjGsOG7m2MgTeG7uSwgU8ahbiBUcsOgLCDEkMOgIE7hurVuZyA1NTAwMDAsIFZp4buHdCBOYW0!5e0!3m2!1svi!2s!4v1671786009182!5m2!1svi!2s\" width=\"784\" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '21517648528.jpg', 1573333, 'Khách Sạn Greenery  là nơi cung cấp dịch vụ lưu  trú lý tưởng cho sự vui vẻ và thư giãn của Quý khách.\r\n\r\nKhách Sạn Greenery  là một nơi nghỉ dưỡng đạt tiêu chuẩn với các dịch vụ tiện nghi như: wifi miễn phí, nước uống miễn phí,... đảm bảo mang đến cho khách hàng sự thoải mái nhất. Với thiết kế thanh lịch và gần gũi', 'Khách Sạn Đà Nẵng, Khách Sạn Giá Rẻ, Khách Sạn 5 Sao, Khách Sạn', 5, 1, '2022-12-23 09:02:17', '2024-11-03 15:48:43', NULL),
(9, 'Mikazuki Japanese', 5, 2, 5, 6, 'Xuân Thiều, Nguyễn Tất Thành, Quận Liên Chiểu, Đà Nẵng, Việt Nam', '16.0934525,108.1439935', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d61330.78870377386!2d108.05897135820311!3d16.108282200000012!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421f1ab2abda73%3A0x51f7f0fd3e3a9f0!2zxJDDrG5oIGzDoG5nIFh1w6JuIFRoaeG7gXU!5e0!3m2!1svi!2s!4v1671787255484!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '_ika932050.jpg', 3851149, 'Với mong muốn mang đến những trải nghiệm thú vị và trọn vẹn nhất cho du khách, Chúng tôi xin thông báo sẽ tạm ngừng các hoạt động vui chơi, giải trí cũng như nhà hàng Nami tại một số khu vực nhằm phục vụ cho công tác bảo trì bảo dưỡng và cải tạo. Thời gian cụ thể như sau:', 'Khách Sạn Đà Nẵng, Khách Sạn Giá Rẻ, Khách Sạn 5 Sao, Khách Sạn', 12, 1, '2022-12-23 09:22:40', '2024-11-03 15:48:43', NULL),
(10, 'Le Sands Oceanfront', 4, 1, 4, 3, '28, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0862038,108.2482873', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.6007127343964!2d108.24597771468444!3d16.08619678887048!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314217f2933aadc9%3A0xe74acb433414a474!2zMjggVsO1IE5ndXnDqm4gR2nDoXAsIE3Dom4gVGjDoWksIFPGoW4gVHLDoCwgxJDDoCBO4bq1bmcgNTUwMDAwLCBWaeG7h3QgTmFt!5e0!3m2!1svi!2s!4v1671819483250!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'le-sands-pool-31.jpg', 4397606, 'Khách Sạn Le Sands Oceanfront Đà Nẵng là nơi cung cấp dịch vụ lưu  trú lý tưởng cho sự vui vẻ và thư giãn của Quý khách.\r\n\r\nKhách Sạn Le Sands Oceanfront Đà Nẵng là một nơi nghỉ dưỡng đạt tiêu chuẩn với các dịch vụ tiện nghi như: wifi miễn phí, nước uống miễn phí,... đảm bảo mang đến cho khách hàng sự thoải mái nhất.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 3, 1, '2022-12-23 18:21:15', '2024-11-03 15:48:43', NULL),
(11, 'Khách Sạn Dana Marina ', 4, 3, 5, 8, '47-49, Võ Văn Kiệt, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0632051,108.2436205', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.0446046670527!2d108.24145801442754!3d16.063174988884622!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421781f43f628f%3A0x834bd8d8b2fc3a8a!2zNDcgVsO1IFbEg24gS2nhu4d0LCBQaMaw4bubYyBN4bu5LCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwLCBWaeG7h3QgTmFt!5e0!3m2!1svi!2s!4v1671820290451!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'b5d9b23f063e07ea6f8f7855e9ce2cd213.jpg', 3643033, 'Đến với Đà Nẵng, trải nghiệm nghỉ dưỡng tại khách sạn bên bờ biển sẽ là điều du khách không nên bỏ qua. Dịch vụ nghỉ dưỡng 4 sao tại khách sạn Dana Marina sẽ đem đến cho bạn những kỷ niệm đáng nhớ. Tiện nghi hiện đại, dịch vụ chuyên nghiệp của khách sạn sẽ đem đến kỳ nghỉ thật trọn vẹn', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 5, 1, '2022-12-23 18:33:25', '2024-11-03 15:48:43', NULL),
(12, 'Khách Sạn Mỹ Khê 2', 3, 2, 6, 3, 'Số 260, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0576447,108.246584', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.1541278315212!2d108.24453961468397!3d16.05748978888817!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314217799fea5be5%3A0x9652c927686996b9!2zMjYwIFbDtSBOZ3V5w6puIEdpw6FwLCBQaMaw4bubYyBN4bu5LCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671820869083!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'z3853685949505_1fee13e181aa11d21e6a45ddcb6c09ba22.jpg', 2907143, 'Khách sạn Mỹ Khê II được tọa lạc trước bãi biển Mỹ Khê xinh đẹp và thơ mộng, một trong những địa điểm thu hút khách du lịch hàng đầu của thành phố Đà Nẵng. Quý khách chỉ đi bộ băng qua đường là đến bãi tắm chính của biển Mỹ Khê. Với quy mô 74 phòng nghỉ đã được nâng cấp mới, khách sạn đạt chuẩn 3 sao đầy đủ tiện nghi phục vụ quý khách hàng trong thời gian nghỉ dưỡng và công tác tại Đà Nẵng.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 9, 1, '2022-12-23 18:42:33', '2024-11-03 15:48:43', NULL),
(13, 'Khách Sạn Bình Dương', 3, 3, 7, 3, '32-34, Trần Phú, Quận Hải Châu, Đà Nẵng, Việt Nam', '16.0741914,108.2235774', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.8321433145784!2d108.22127641442776!3d16.074197988877835!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31421830644a7547%3A0xef2001d39313c4e7!2zMzIgxJAuIFRy4bqnbiBQaMO6LCBI4bqjaSBDaMOidSAxLCBI4bqjaSBDaMOidSwgxJDDoCBO4bq1bmcgNTUwMDAwLCBWaeG7h3QgTmFt!5e0!3m2!1svi!2s!4v1671821533142!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '1395914098.jpg', 2867667, 'Khách Sạn Bình Dương là nơi cung cấp dịch vụ lưu  trú lý tưởng cho sự vui vẻ và thư giãn của Quý khách.\r\n\r\nKhách Sạn Bình Dương là một nơi nghỉ dưỡng đạt tiêu chuẩn với các dịch vụ tiện nghi như: wifi miễn phí, nước uống miễn phí,... đảm bảo mang đến cho khách hàng sự thoải mái nhất', 'Khách Sạn Đà Nẵng, Khách Sạn 3 Sao, Khách Sạn Giá Tốt', 2, 1, '2022-12-23 18:53:33', '2024-11-03 15:48:43', NULL),
(14, 'Khách Sạn FIVITEL Queen', 3, 2, 6, 3, '155-157, Lê Quang Đạo, Quận Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.0508078,108.2453481', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.281604281671!2d108.24325151468386!3d16.05087018889228!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142177b3441c391%3A0xea7f70a7b0426889!2zMTU1LCAxNTcgTMOqIFF1YW5nIMSQ4bqhbywgQuG6r2MgTeG7uSBQaMO6LCBOZ8WpIEjDoG5oIFPGoW4sIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671822116971!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '279.jpg', 2290768, 'Để đồng nhất thương hiệu cho FVG Travel nên Khách sạn Queen\'s Finger được đổi tên thành khách sạn FIVITEL Queen.', 'Khách Sạn Đà Nẵng, Khách Sạn 3 Sao, Khách Sạn Giá Tốt', 4, 1, '2022-12-23 19:03:13', '2024-11-03 15:48:43', NULL),
(15, 'Four Points by Sheraton', 5, 2, 2, 3, '118 - 120, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0778929,108.2453039', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.7643833582556!2d108.24307691468428!3d16.0777119888757!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142178e95bda349%3A0x61ebd93becf8f96d!2zMTE4LCAxMjAgVsO1IE5ndXnDqm4gR2nDoXAsIFN0cmVldCwgU8ahbiBUcsOgLCDEkMOgIE7hurVuZyA1NTAwMDAsIFZp4buHdCBOYW0!5e0!3m2!1svi!2s!4v1671848960102!5m2!1svi!2s\" width=\"784 \" height=\"146 \" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '33.jpg', 2921454, 'Four Points by Sheraton Danang tọa lạc tại khu Bãi biển Mỹ Khê thuộc thành phố Đà Nẵng, nằm trong bán kính 2 km từ Cầu Sông Hàn và 2,3 km từ Cầu tàu Tình yêu. Khách sạn nằm cách Trung tâm thương mại Indochina Riverside 2,3 km, cách Bảo tàng Chăm 3,1 km, Công viên Châu Á 5 km và Sân bay Quốc tế Đà Nẵng 6 km.', 'Khách Sạn Đà Nẵng, Khách Sạn 5 Sao, Khách Sạn Giá Tốt', 2, 1, '2022-12-24 02:31:37', '2024-11-03 15:48:43', NULL),
(16, 'Khách sạn Mandila Beach', 5, 3, 8, 8, '218, Võ Nguyên Giáp, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0674405,108.2447535', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.761313186105!2d108.24321091442785!3d16.07787118887561!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142178ebc260505%3A0xc6eeac18a1830e50!2sFour%20Points%20by%20Sheraton%20Danang!5e0!3m2!1svi!2s!4v1671849575027!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'SVoDajCBSZmO4UvOc9ISLg-253.jpeg', 3088288, 'Khách Sạn Mandila Beach Đà Nẵng Tọa lạc tại ví trị đắc địa trên con đường vàng Võ Nguyên Giáp, với tầm nhìn ôm trọn một trong những bờ biển đẹp nhất hành tinh quanh năm cát trắng mịn và nước trong xanh, Khách Sạn Mandila Beach Đà Nẵng là một trong những địa điểm nghỉ dưỡng lý tưởng khi đến với thành phố Đà Nẵng.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 5, 1, '2022-12-24 02:41:11', '2024-11-03 15:48:43', NULL),
(17, 'Đà Nẵng Golden Bay', 5, 1, 5, 8, '01, Lê Văn Duyệt, Quận Sơn Trà, Đà Nẵng, Việt Nam', '16.0976983,108.2245591', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.396521732398!2d108.22265851442806!3d16.096776088863894!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142181010ded0b9%3A0xb537e6de9fb098dc!2zMDEgTMOqIFbEg24gRHV54buHdCwgTuG6oWkgSGnDqm4gxJDDtG5nLCBTxqFuIFRyw6AsIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671850154078!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '29403_QGEQ43WK47_2710.jpg', 3057143, 'Danang Golden Bay – khách sạn 5 sao với những dịch vụ nghỉ dưỡng sang trọng và đẳng cấp. Sở hữu địa thế tuyệt vời nơi của dòng sông Hàn đổ ra biển Đông xanh ngắt, khách sạn Danang Golden Bay là điểm giao thoa hòa hợp giữa núi, trời và biển, là địa điểm lý tưởng khởi đầu cho hành trình khám phá thành phố Đà Nẵng năng động, vẻ đẹp quyến rũ của biển Đà Nẵng', 'Khách Sạn Đà Nẵng, Khách Sạn 5 Sao, Khách Sạn Giá Tốt', 14, 1, '2022-12-24 02:50:43', '2024-11-03 15:48:43', NULL),
(18, 'Cicilia Hotels & Spa Danang', 4, 1, 4, 7, '6-8-10, Đỗ Bá, Quận Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.052111,108.2466021', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.258736005639!2d108.2443832146839!3d16.052057888891543!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142177ae0bde10f%3A0x1b8b3008a40e9c3f!2sCicilia%20Danang%20Hotel%20%26%20Spa!5e0!3m2!1svi!2s!4v1671850652662!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'ES9WIGpST-SXFNLIUU-QWw-3348.jpeg', 2625000, 'Khách sạn nằm ở vị trí lý tưởng cách Trung tâm Thành phố Đà Nẵng và Nhà thờ Con Gà 10 phút di chuyển bằng ô tô hoặc xe máy, cách Bãi biển Mỹ Khê 350m. Ga Tàu Đà Nẵng và Ngũ Hành Sơn đều cách khách sạn 6,4km và Sân bay Quốc tế Đà Nẵng cách khách sạn 5km.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 6, 1, '2022-12-24 02:59:36', '2024-11-03 15:48:43', NULL),
(19, 'The Blossom Resort Island', 4, 1, 3, 4, 'Lô A1-a2, Khu Biệt Thự Đảo Xanh Mở Rộng, Khu Đảo Xanh, Quận Hải Châu, Đà Nẵng, Việt Nam', '16.0450781,108.2269224', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.3938326821412!2d108.2247702146838!3d16.04504018889589!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314219dca34ae1d3%3A0x66a4d38a6e610248!2sThe%20Blossom%20Resort%20Island%20-%20All%20Inclusive!5e0!3m2!1svi!2s!4v1671851185849!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'poolside8-253.jpeg', 2320250, 'Tọa lạc ở vị trí đẹp của Sông Hàn, The Blossom Resort Da Nang hưởng được rất nhiều lợi thế trong mua sắm, nhà hàng, ngắm cảnh trung tâm của Đà Nẵng. Chỗ nghỉ này cách cầu Sông Hàn 800 m và Bảo tàng Chăm 900 m. Khu nghỉ dưỡng cách trung tâm thành phố khoảng 5 km và cách sân bay khoảng 12 phút lái xe.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 17, 1, '2022-12-24 03:09:05', '2024-11-03 15:48:43', NULL),
(20, 'Khách Sạn Eden Ocean View', 4, 1, 7, 7, '294, Võ Nguyên Giáp, Quận Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.0509917,108.248221', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.3938326821412!2d108.2247702146838!3d16.04504018889589!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142177ab7d9d951%3A0x2a718695d5b10c9a!2zMjk0IFbDtSBOZ3V5w6puIEdpw6FwLCBC4bqvYyBN4bu5IFBow7osIE5nxakgSMOgbmggU8ahbiwgxJDDoCBO4bq1bmcgNTUwMDAwLCBWaeG7h3QgTmFt!5e0!3m2!1svi!2s!4v1671851707301!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', 'PkUzwx9MRvCveZg2Vnl76w-6-_DSC008047.jpeg', 2026580, 'Tọa lạc tại thành phố Đà Nẵng, cách Bãi biển Mỹ Khê vài bước chân, cách Bãi biển Bắc Mỹ An 1 km và Cầu tàu Tình yêu 3,6 km. Sân bay gần nhất là sân bay quốc tế Đà Nẵng, nằm trong bán kính 6 km từ Eden Hotel Danang.', 'Khách Sạn Đà Nẵng, Khách Sạn 4 Sao, Khách Sạn Giá Tốt', 14, 1, '2022-12-24 03:18:44', '2024-11-03 15:48:43', NULL),
(21, 'Risemount Premier Resort ', 5, 1, 5, 7, '120, Nguyễn Văn Thoại, Quận Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.0546597,108.2420544', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3834.279975426385!2d108.24598931442742!3d16.050954788892227!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3142177c0d456ba9%3A0x1a61830469193649!2zMTIwIE5ndXnhu4VuIFbEg24gVGhv4bqhaSwgQuG6r2MgTeG7uSBQaMO6LCBOZ8WpIEjDoG5oIFPGoW4sIMSQw6AgTuG6tW5nIDU1MDAwMCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1671852321561!5m2!1svi!2s\" width=\"784 \" height=\"146\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '22811_HM3SP0T5F3_10200745570.jpg', 1715143, 'Những năm gần đây du lịch Đà Nẵng phát triển mạnh mẽ, nhanh đến chóng mặt. Đà Nẵng đã trở thành điểm đến của hàng triệu khách du lịch trong và ngoài nước. Xuất phát từ nhu cầu nghỉ ngơi của du khách, Risemount Premier Resort Đà Nẵng ngày một hiện đại hơn', 'Khách Sạn 5 Sao, Khách Sạn Đà Nẵng, Khách Sạn Giá Tốt', 10, 1, '2022-12-24 03:26:41', '2024-11-03 15:48:43', NULL),
(22, 'Hải Âu Hotel', 3, 1, 5, 7, '576 Cửa Đại, Cẩm Châu, Hội An, Quảng Nam 560000, Việt Nam', 'https://maps.app.goo.gl/GvPJmkJ4vhQMNuQz6', '<iframe src=\"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3837.5606198475!2d108.33384370983397!3d15.879673984709122!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31420dd6904e5017%3A0xc23e88aebfbacfa7!2sHai%20Au%20boutique%20hotel!5e0!3m2!1svi!2s!4v1759760387365!5m2!1svi!2s\" width=\"600\" height=\"450\" style=\"border:0;\" allowfullscreen=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer-when-downgrade\"></iframe>', '8073524075.jpg', NULL, 'Khách sạn có không gian thư thái, cách Bảo tàng Văn hóa Sa Huỳnh và Hội quán Quảng Đông 15 phút đi bộ, cách bãi biển Cửa Đại 5 km.\r\nPhòng ở bình dân, sáng sủa, có ban công, Wi-Fi, TV màn hình phẳng, dụng cụ pha trà và cà phê, bàn làm việc, tủ lạnh nhỏ và két an toàn. Khách sạn phục vụ ăn uống tại phòng.\r\nKhách sạn có các tiện nghi như nhà hàng với không gian thư thái, bể bơi ngoài trời, sân hiên và dịch vụ cho thuê xe đạp. Có chỗ đậu xe và bữa sáng tự chọn.', 'HaiAuHotel, 3sao', 0, 1, '2025-10-06 14:34:34', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_manipulation_activity`
--

CREATE TABLE `tbl_manipulation_activity` (
  `manipulation_activity_id` int(10) NOT NULL,
  `manipulation_activity_admin_id` int(11) DEFAULT NULL,
  `manipulation_activity_admin_name` varchar(256) DEFAULT NULL,
  `manipulation_activity_customer_id` int(11) DEFAULT NULL,
  `manipulation_activity_customer_name` varchar(255) DEFAULT NULL,
  `manipulation_activity_type` int(11) NOT NULL,
  `manipulation_activity_action` text NOT NULL,
  `manipulation_activity_ip` varchar(256) NOT NULL,
  `manipulation_activity_located` varchar(256) NOT NULL,
  `manipulation_activity_device` varchar(256) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_menu_restaurant`
--

CREATE TABLE `tbl_menu_restaurant` (
  `menu_item_id` int(11) NOT NULL,
  `restaurant_id` int(11) DEFAULT NULL,
  `menu_item_name` varchar(255) NOT NULL,
  `menu_item_image` varchar(255) NOT NULL,
  `menu_item_description` varchar(255) NOT NULL,
  `menu_item_price` double DEFAULT NULL,
  `menu_item_status` int(1) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_menu_restaurant`
--

INSERT INTO `tbl_menu_restaurant` (`menu_item_id`, `restaurant_id`, `menu_item_name`, `menu_item_image`, `menu_item_description`, `menu_item_price`, `menu_item_status`, `created_at`, `updated_at`) VALUES
(4, 1, 'Thịt luộc mắm tôm', 'bepviet2071-copy-802834.jpg', 'Là sự hòa quyện của thịt luộc với mắm tôm', 119000, 1, '2024-10-15 16:53:51', '2024-10-15 16:53:51'),
(5, 1, 'Rau đảo phú quý', 'rau-tron-24114.jpg', 'Rau trộn được nhập từ đảo Phú Quý', 109000, 1, '2024-10-15 16:54:34', '2024-10-15 16:54:34'),
(6, 1, 'Cá kho tiêu', '4318877543925966803532242640667737108045506n-565084.jpg', 'Cá chốt kho tiêu rất thơm', 160000, 1, '2024-10-15 16:55:05', '2024-10-15 16:55:05'),
(7, 1, 'Canh cua rau đay', 'bepviet2297-copy-72285.jpg', 'Canh cua được nấu với rau đay', 130000, 1, '2024-10-15 16:55:38', '2024-10-15 16:55:38'),
(8, 1, 'Canh chua cá bớp', 'bepviet1816-copy-614541.jpg', 'Canh chua được nấu với cá bớp thơm ngon', 230000, 1, '2024-10-15 16:56:25', '2024-10-15 16:56:25'),
(9, 1, 'Canh khổ qua', 'canh-kho-qua-524348.jpg', 'Canh khổ qua được nấu cùng thác lác', 110000, 1, '2024-10-15 16:57:09', '2024-10-15 16:57:09'),
(10, 1, 'Cà tím sốt thịt', 'bepviet2305-copy-536958.jpg', 'Cà tím được nấu cùng sốt thịt bằm', 130000, 1, '2024-10-15 16:58:02', '2024-10-15 16:58:02'),
(11, 1, 'Cá bớp kho tiêu', 'bepviet1959-copy-186251.jpg', 'Cá bớp kho thơm cùng tiêu', 130000, 1, '2024-10-15 17:01:58', '2024-10-15 17:01:58'),
(12, 4, 'Gỏi cuốn', 'Screenshot_16-10-2024_0336_danang25.jpeg', 'Gỏi chấm hòa quyện với nước mắm', 60000, 1, '2024-10-15 17:35:31', '2024-10-15 17:35:31'),
(13, 4, 'Cơm chiên', 'Screenshot_16-10-2024_0342_danang3.jpeg', 'Gỏi chấm hòa quyện với nước mắm', 90000, 1, '2024-10-15 17:37:37', '2024-10-15 17:37:37'),
(14, 4, 'Chả giò', 'Screenshot_16-10-2024_03136_danang8.jpeg', 'Chả giò giống với gỏi cuốn', 85000, 1, '2024-10-15 17:38:19', '2024-10-15 17:38:19'),
(15, 4, 'Chả lụi', 'Screenshot_16-10-2024_03250_danang69.jpeg', 'Giống với chả giò', 130000, 1, '2024-10-15 17:38:48', '2024-10-15 17:38:48'),
(16, 4, 'Bún thịt xào', 'Screenshot_16-10-2024_03320_danang15.jpeg', 'Là sự hòa quyện giữa nhiều hương vị', 60000, 1, '2024-10-15 17:39:31', '2024-10-15 17:39:31'),
(17, 4, 'Bún Chả giò', 'Screenshot_16-10-2024_03334_danang70.jpeg', 'Là sự kết hợp hoàn hảo giữa bún và chả giò', 70000, 1, '2024-10-15 17:40:12', '2024-10-15 17:40:12'),
(18, 4, 'Bún bò Huế', 'Screenshot_16-10-2024_03350_danang36.jpeg', 'Là một đặc sản xứ Huế', 75000, 1, '2024-10-15 17:40:45', '2024-10-15 17:40:45'),
(19, 5, 'Điệp Pháp', 'Screenshot_16-10-2024_05054_www44.jpeg', 'Điệp được nhập từ Pháp', 200000, 1, '2024-10-15 17:57:28', '2024-10-15 17:57:28'),
(20, 5, 'Beefsteak Cheese', 'Screenshot_16-10-2024_05117_www12.jpeg', 'Nhập từ bò thượng hạng', 700000, 1, '2024-10-15 17:58:22', '2024-10-15 17:58:22'),
(21, 5, 'Mực nhồi thịt', 'Screenshot_16-10-2024_05140_www21.jpeg', 'Mực được hầm cùng với thịt', 570000, 1, '2024-10-15 17:59:50', '2024-10-15 17:59:50'),
(22, 5, 'Mực sốt cà', 'Screenshot_16-10-2024_0523_www49.jpeg', 'Hòa quyện với hương vị cà chua', 590000, 1, '2024-10-15 18:00:34', '2024-10-15 18:00:34'),
(23, 5, 'Buttcher Steak', 'Screenshot_16-10-2024_05316_www10.jpeg', 'Được cắt từng lát ăn cùng với khoai tây', 760000, 1, '2024-10-15 18:01:58', '2024-10-15 18:01:58'),
(24, 5, 'Gan Ngỗng', 'Screenshot_16-10-2024_05421_www54.jpeg', 'Được chọn từ các con ngỗng Pháp', 470000, 1, '2024-10-15 18:02:42', '2024-10-15 18:02:42'),
(25, 5, 'Tôm hùm', 'Screenshot_16-10-2024_1333_cabanonpalace64.jpeg', 'Tôm hùm tươi', 2500000, 1, '2024-10-15 18:04:39', '2024-10-15 18:04:39'),
(26, 6, 'Chả hải sản', 'Screenshot_16-10-2024_205615_docs40.jpeg', 'Chả hải sản được bọc lá chuối nướng', 119000, 1, '2024-10-16 13:57:58', '2024-10-16 13:57:58'),
(27, 6, 'Thịt xá xíu', 'Screenshot_16-10-2024_205816_docs46.jpeg', 'Thịt xá xíu được nấu theo kiểu Thái', 105000, 1, '2024-10-16 13:59:10', '2024-10-16 13:59:10'),
(28, 6, 'Ram chả kiểu thái', 'Screenshot_16-10-2024_205928_docs56.jpeg', 'Là 1 set món chiên kiểu Thái', 119000, 1, '2024-10-16 14:00:13', '2024-10-16 14:00:13'),
(29, 6, 'Trứng chả bắc thảo', 'Screenshot_16-10-2024_21034_docs30.jpeg', 'Trứng bắc thảo được nấu cùng với chả', 85000, 1, '2024-10-16 14:01:12', '2024-10-16 14:01:12'),
(30, 6, 'Trứng chiên xốt thái', 'Screenshot_16-10-2024_21139_docs42.jpeg', 'Trứng chiên xốt thái quế', 39000, 1, '2024-10-16 14:02:25', '2024-10-16 14:02:25'),
(31, 6, 'Xúc xích tươi', 'Screenshot_16-10-2024_21252_docs43.jpeg', 'Xúc xích tươi Chăng Mai', 99000, 1, '2024-10-16 14:03:50', '2024-10-16 14:03:50'),
(32, 6, 'Gà nướng', 'Screenshot_16-10-2024_21410_docs30.jpeg', 'Gà nướng bó xôi', 259000, 1, '2024-10-16 14:04:46', '2024-10-16 14:04:46'),
(33, 6, 'Heo nướng mọi', 'Screenshot_16-10-2024_21510_docs20.jpeg', 'Heo nướng mọi ăn cùng với xôi', 189000, 1, '2024-10-16 14:05:54', '2024-10-16 14:05:54'),
(34, 7, 'Tokyo BBQ', 'Screenshot_16-10-2024_211840_docs23.jpeg', 'Sườn bò, lưỡi bò, vai bò', 609000, 1, '2024-10-16 14:19:29', '2024-10-16 14:19:29'),
(35, 7, 'Matsu BBQ', 'Screenshot_16-10-2024_211950_docs47.jpeg', 'Món nướng với thịu cừu, ba rọi', 299000, 1, '2024-10-16 14:20:42', '2024-10-16 14:20:42'),
(36, 7, 'Hàu đút lò', 'Screenshot_16-10-2024_212115_docs91.jpeg', 'Hàu sữa ngũ vị đút lò', 209000, 1, '2024-10-16 14:21:53', '2024-10-16 14:21:53'),
(37, 7, 'Sò điệp nướng', 'Screenshot_16-10-2024_21229_docs71.jpeg', 'Sò điệp nướng mỡ hành', 159000, 1, '2024-10-16 14:22:43', '2024-10-16 14:22:43'),
(38, 7, 'Combo hun khói', 'Screenshot_16-10-2024_21235_docs27.jpeg', 'Sườn hun khói, xúc xích vua, khoai tây chiên', 419000, 1, '2024-10-16 14:24:03', '2024-10-16 14:24:03'),
(39, 7, 'Combo nướng lu', 'Screenshot_16-10-2024_212425_docs98.jpeg', 'Sườn hun khói, xúc xích vua, khoai tây chiên', 369000, 1, '2024-10-16 14:25:05', '2024-10-16 14:25:05'),
(40, 8, 'Cơm cháy Madam Lân', 'Screenshot_16-10-2024_214019_madamelan38.jpeg', 'Cơm cháy do Madam Lân sáng tạo', 69000, 1, '2024-10-16 14:41:14', '2024-10-16 14:41:14'),
(41, 8, 'Bắp Hoa ôm dầu', 'Screenshot_16-10-2024_214129_madamelan14.jpeg', 'Bắp hoa ôm xì dầu', 280000, 1, '2024-10-16 14:42:05', '2024-10-16 14:42:05'),
(42, 8, 'Canh chua chả cá', 'Screenshot_16-10-2024_214221_madamelan30.jpeg', 'Canh chua được nấu cùng chả cá', 235000, 1, '2024-10-16 14:43:01', '2024-10-16 14:43:01'),
(43, 8, 'Nem rán', 'Screenshot_16-10-2024_214340_madamelan66.jpeg', 'Nem rán Madam Lân', 235000, 1, '2024-10-16 14:44:14', '2024-10-16 14:44:14'),
(44, 8, 'Bánh mì bò kho', 'Screenshot_16-10-2024_214427_madamelan34.jpeg', 'Một món ăn quen thuộc của Việt Nam', 82000, 1, '2024-10-16 14:45:07', '2024-10-16 14:45:07'),
(45, 8, 'Sò điệp nướng', 'Screenshot_16-10-2024_214523_madamelan17.jpeg', 'Sò điệp nướng bơ', 449000, 1, '2024-10-16 14:45:58', '2024-10-16 14:45:58'),
(46, 8, 'Cá mú nướng', 'Screenshot_16-10-2024_214619_madamelan18.jpeg', 'Cá mú nướng song vị', 310000, 1, '2024-10-16 14:46:49', '2024-10-16 14:46:49'),
(47, 8, 'Tôm hùm Baby', 'Screenshot_16-10-2024_21474_madamelan4.jpeg', 'Tôm hùm bayby sốt gạch đỏ', 278000, 1, '2024-10-16 14:47:51', '2024-10-16 14:47:51'),
(48, 9, 'Mỳ Quảng tôm thịt', 'Screenshot_16-10-2024_215733_docs70.jpeg', 'Mỳ Quảng tôm thịt theo kiểu Nghệ', 65000, 1, '2024-10-16 14:58:27', '2024-10-16 14:58:27'),
(49, 9, 'Gà hấp mắm nhĩ', 'Screenshot_16-10-2024_215941_docs36.jpeg', 'Gà hấp với mắm nhĩ', 430000, 1, '2024-10-16 15:00:25', '2024-10-16 15:00:25'),
(50, 9, 'Chả giò làng Nghệ', 'Screenshot_16-10-2024_22041_docs74.jpeg', 'Chả giò của Nghệ', 175000, 1, '2024-10-16 15:01:27', '2024-10-16 15:01:27'),
(51, 9, 'Salad rong nho', 'Screenshot_16-10-2024_22353_docs4.jpeg', 'Salad rong nho cá ngừ', 135000, 1, '2024-10-16 15:04:40', '2024-10-16 15:04:40'),
(52, 9, 'Cải thìa sốt mắm', 'Screenshot_16-10-2024_22458_docs4.jpeg', 'Cải thìa cùng với nấm', 105000, 1, '2024-10-16 15:05:35', '2024-10-16 15:05:35'),
(53, 9, 'Mẹt gà 5 món', 'Screenshot_16-10-2024_2263_docs2.jpeg', 'Mẹt gà cùng 5 món ăn đã cái nư', 460000, 1, '2024-10-16 15:07:17', '2024-10-16 15:07:17'),
(54, 9, 'Cơm chiên hải sản', 'Screenshot_16-10-2024_22731_docs99.jpeg', 'Cơm chiên hải sản gồm tôm, cua,...', 105000, 1, '2024-10-16 15:08:05', '2024-10-16 15:08:05'),
(55, 9, 'Súp nấm tuyết hoa', 'Screenshot_16-10-2024_22824_docs17.jpeg', 'Món ăn chay cho người tu dưỡng', 59000, 1, '2024-10-16 15:09:14', '2024-10-16 15:09:14'),
(56, 9, 'Cơm hấp hạt sen', 'Screenshot_16-10-2024_22950_docs28.jpeg', 'Cơm xào được hấp cùng với hạt sen thơm ngon', 89000, 1, '2024-10-16 15:10:49', '2024-10-16 15:10:49');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_order`
--

CREATE TABLE `tbl_order` (
  `order_id` int(11) NOT NULL,
  `start_day` varchar(256) NOT NULL,
  `end_day` varchar(256) DEFAULT NULL,
  `orderer_id` int(11) NOT NULL,
  `payment_id` int(11) NOT NULL,
  `order_status` int(1) DEFAULT NULL,
  `order_code` varchar(256) DEFAULT NULL,
  `coupon_name_code` varchar(256) DEFAULT NULL,
  `coupon_sale_price` double DEFAULT NULL,
  `total_price` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL,
  `order_type` int(1) NOT NULL,
  `restaurant_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_order`
--

INSERT INTO `tbl_order` (`order_id`, `start_day`, `end_day`, `orderer_id`, `payment_id`, `order_status`, `order_code`, `coupon_name_code`, `coupon_sale_price`, `total_price`, `created_at`, `updated_at`, `deleted_at`, `order_type`, `restaurant_id`) VALUES
(31, '05-05-2024', '06-05-2024', 31, 33, 2, 'MYHOTEL2607', 'HELLOVKU', 304000, 0, '2024-05-05 12:56:02', '2024-05-05 13:03:35', NULL, 0, 0),
(32, '09-05-2024', '11-05-2024', 32, 34, -2, 'MYHOTEL2538', 'CHAODANANG', 232664.3352, 0, '2024-05-05 13:13:33', '2024-10-29 15:53:38', NULL, 0, 0),
(33, '10-05-2024', '16-05-2024', 33, 35, 2, 'MYHOTEL7530', 'HELLOVKU', 1488425.04, 0, '2024-05-06 08:33:38', '2024-05-06 18:32:07', NULL, 0, 0),
(34, '19-05-2024', '21-05-2024', 34, 36, 0, 'MYHOTEL432', 'HELLOVKU', 788500, 0, '2024-05-06 10:05:11', '2024-05-06 15:19:01', NULL, 0, 0),
(49, '12-05-2024', '14-05-2024', 49, 51, 0, 'MYHOTEL6269', 'CHAODANANG', 2318680, 0, '2024-05-12 15:22:50', NULL, NULL, 0, 0),
(50, '12-05-2024', '14-05-2024', 50, 52, 0, 'MYHOTEL7419', 'HELLOVKU', 484120, 0, '2024-05-12 15:47:42', NULL, NULL, 0, 0),
(51, '24-05-2024', '26-05-2024', 51, 53, -2, 'MYHOTEL8735', 'CHAODANANG', 229320, 0, '2024-05-21 17:03:33', '2024-10-29 15:44:30', NULL, 0, 0),
(52, '07-06-2024', '09-06-2024', 52, 54, -2, 'MYHOTEL9671', 'CHAODANANG', 222199.2, 0, '2024-06-04 11:33:55', '2024-06-04 11:53:22', NULL, 0, 0),
(57, '07-06-2024', '09-06-2024', 57, 59, 0, 'MYHOTEL8696', 'Không có', 0, 0, '2024-06-04 12:11:19', NULL, NULL, 0, 0),
(58, '04-06-2024', '05-06-2024', 58, 60, -2, 'MYHOTEL9000', 'HELLOVKU', 394250, 0, '2024-06-04 12:41:11', '2024-06-04 12:46:49', NULL, 0, 0),
(59, '07-06-2024', '12-06-2024', 59, 61, 1, 'MYHOTEL2930', 'CHAODANANG', 684000, 0, '2024-06-04 12:54:36', '2024-06-04 12:59:09', NULL, 0, 0),
(60, '05-10-2024', '07-10-2024', 60, 62, 0, 'MYHOTEL9254', 'CHAODANANG', 607042.8, 0, '2024-10-05 03:41:28', NULL, NULL, 0, 0),
(61, '2024-10-29 17:15:00.000', NULL, 64, 67, 0, 'MYHOTEL+20241028151241', NULL, NULL, 235000, '2024-10-28 15:12:41', '2024-10-30 15:12:23', NULL, 1, 4),
(62, '2024-10-29 17:15:00.000', NULL, 65, 68, 0, 'MYHOTEL20241028151302', NULL, NULL, 235000, '2024-10-28 15:13:02', '2024-10-30 15:12:21', NULL, 1, 4),
(63, '2024-10-29 14:45:00.000', NULL, 66, 69, 0, 'MYHOTEL20241028154834', NULL, NULL, 340000, '2024-10-28 15:48:34', '2024-10-30 15:12:19', NULL, 1, 4),
(64, '2024-10-29 14:45:00.000', NULL, 67, 70, -2, 'MYHOTEL20241028154853', NULL, NULL, 340000, '2024-10-28 15:48:53', '2024-11-12 16:09:10', NULL, 1, 4),
(65, '2024-10-29 14:45:00.000', NULL, 68, 71, 0, 'MYHOTEL20241028154947', NULL, NULL, 340000, '2024-10-28 15:49:47', '2024-10-30 15:12:15', NULL, 1, 4),
(66, '2024-10-29 14:45:00.000', NULL, 69, 72, 0, 'MYHOTEL20241028155620', NULL, NULL, 340000, '2024-10-28 15:56:20', '2024-10-30 15:12:13', NULL, 1, 4),
(67, '2024-10-29 17:00:00.000', NULL, 70, 73, 0, 'MYHOTEL20241028160041', NULL, NULL, 340000, '2024-10-28 16:00:41', '2024-10-30 15:12:10', NULL, 1, 4),
(68, '2024-10-29 17:00:00.000', NULL, 71, 74, 0, 'MYHOTEL20241028160238', NULL, NULL, 340000, '2024-10-28 16:02:38', '2024-10-30 15:12:08', NULL, 1, 4),
(69, '2024-10-29 17:00:00.000', NULL, 72, 75, 0, 'MYHOTEL20241028160300', NULL, NULL, 340000, '2024-10-28 16:03:00', '2024-10-30 15:12:05', NULL, 1, 4),
(70, '2024-10-29 17:00:00.000', NULL, 73, 76, 0, 'MYHOTEL20241028160336', NULL, NULL, 340000, '2024-10-28 16:03:36', '2024-10-30 15:11:57', NULL, 1, 4),
(71, '2024-10-29 17:00:00.000', NULL, 74, 77, 0, 'MYHOTEL20241028160349', NULL, NULL, 340000, '2024-10-28 16:03:50', '2024-10-30 15:11:56', NULL, 1, 4),
(72, '2024-10-29 14:00:00.000', NULL, 75, 78, 0, 'MYHOTEL20241028161603', NULL, NULL, 570000, '2024-10-28 16:16:03', '2024-10-30 15:11:54', NULL, 1, 4),
(73, '2024-10-29 14:00:00.000', NULL, 76, 79, 0, 'MYHOTEL20241028161701', NULL, NULL, 570000, '2024-10-28 16:17:01', '2024-10-30 15:11:52', NULL, 1, 4),
(74, '2024-10-29 14:00:00.000', NULL, 77, 80, 0, 'MYHOTEL20241028161735', NULL, NULL, 570000, '2024-10-28 16:17:35', '2024-10-30 15:11:50', NULL, 1, 4),
(75, '2024-10-29 14:00:00.000', NULL, 78, 81, 0, 'MYHOTEL20241028161957', NULL, NULL, 570000, '2024-10-28 16:19:57', '2024-10-30 15:11:49', NULL, 1, 4),
(76, '2024-10-29 14:00:00.000', NULL, 79, 82, 0, 'MYHOTEL20241028162020', NULL, NULL, 570000, '2024-10-28 16:20:20', '2024-10-30 15:11:47', NULL, 1, 4),
(77, '2024-10-29 14:00:00.000', NULL, 80, 83, 0, 'MYHOTEL20241028162052', NULL, NULL, 570000, '2024-10-28 16:20:52', '2024-10-30 15:11:44', NULL, 1, 4),
(78, '2024-10-29 14:00:00.000', NULL, 81, 84, 0, 'MYHOTEL20241028162109', NULL, NULL, 570000, '2024-10-28 16:21:09', '2024-10-30 15:11:42', NULL, 1, 4),
(79, '2024-10-29 15:00:00.000', NULL, 82, 85, 0, 'MYHOTEL20241028162339', NULL, NULL, 235000, '2024-10-28 16:23:39', '2024-10-30 15:11:41', NULL, 1, 4),
(80, '2024-10-29 15:00:00.000', NULL, 83, 86, 0, 'MYHOTEL20241028162708', NULL, NULL, 235000, '2024-10-28 16:27:08', '2024-10-30 15:11:39', NULL, 1, 4),
(81, '2024-10-29 15:00:00.000', NULL, 84, 87, 0, 'MYHOTEL20241028162815', NULL, NULL, 235000, '2024-10-28 16:28:15', '2024-10-30 15:11:36', NULL, 1, 4),
(82, '2024-10-29 15:00:00.000', NULL, 85, 88, 0, 'MYHOTEL20241028162834', NULL, NULL, 235000, '2024-10-28 16:28:35', '2024-10-30 15:11:38', NULL, 1, 4),
(83, '2024-10-29 15:00:00.000', NULL, 86, 89, -2, 'MYHOTEL20241028162929', NULL, NULL, 235000, '2024-10-28 16:29:29', '2024-11-13 00:40:22', NULL, 1, 4),
(84, '2024-10-29 15:00:00.000', NULL, 87, 90, 1, 'MYHOTEL20241028163031', NULL, NULL, 235000, '2024-10-28 16:30:31', '2024-11-05 17:01:37', NULL, 1, 4),
(85, '2024-10-29 15:00:00.000', NULL, 88, 91, -2, 'MYHOTEL20241028163031', NULL, NULL, 235000, '2024-10-28 16:30:31', '2024-11-12 16:09:16', NULL, 1, 4),
(86, '2024-10-29 15:00:00.000', NULL, 89, 92, -2, 'MYHOTEL20241028163053', NULL, NULL, 235000, '2024-10-28 16:30:54', '2024-10-30 16:40:12', NULL, 1, 4),
(87, '2024-10-29 15:00:00.000', NULL, 90, 93, -2, 'MYHOTEL20241028163138', NULL, NULL, 235000, '2024-10-28 16:31:38', '2024-10-30 16:39:35', NULL, 1, 4),
(88, '2024-10-29 15:00:00.000', NULL, 91, 94, -2, 'MYHOTEL20241028163234', NULL, NULL, 235000, '2024-10-28 16:32:34', '2024-10-30 16:39:12', NULL, 1, 4),
(89, '2024-10-29 15:00:00.000', NULL, 92, 95, -2, 'MYHOTEL20241028163403', NULL, NULL, 235000, '2024-10-28 16:34:03', '2024-10-30 16:36:52', NULL, 1, 4),
(90, '2024-10-29 15:00:00.000', NULL, 93, 96, -2, 'MYHOTEL20241028163412', NULL, NULL, 235000, '2024-10-28 16:34:12', '2024-10-30 16:36:05', NULL, 1, 4),
(91, '2024-10-29 15:00:00.000', NULL, 94, 97, -2, 'MYHOTEL20241028163434', NULL, NULL, 235000, '2024-10-28 16:34:34', '2024-10-30 16:33:15', NULL, 1, 4),
(92, '2024-10-29 15:00:00.000', NULL, 95, 98, -2, 'MYHOTEL20241028163714', NULL, NULL, 235000, '2024-10-28 16:37:14', '2024-10-30 16:32:38', NULL, 1, 4),
(93, '2024-10-29 16:00:00.000', NULL, 96, 99, -2, 'MYHOTEL20241028175233', NULL, NULL, 365000, '2024-10-28 17:52:33', '2024-10-30 16:28:12', NULL, 1, 4),
(94, '2024-10-29 18:00:00.000', NULL, 97, 100, -2, 'MYHOTEL20241028175344', NULL, NULL, 235000, '2024-10-28 17:53:44', '2024-10-30 16:27:55', NULL, 1, 4),
(95, '07-11-2024', '09-11-2024', 104, 107, 0, 'MYHOTEL7770', 'CHAODANANG', 229500, 2601000, '2024-11-05 16:06:27', NULL, NULL, 0, NULL),
(96, '07-11-2024', '09-11-2024', 105, 108, 0, 'MYHOTEL6507', 'CHAODANANG', 229500, 2601000, '2024-11-05 16:06:40', NULL, NULL, 0, NULL),
(97, '07-11-2024', '09-11-2024', 106, 109, 0, 'MYHOTEL2476', 'CHAODANANG', 229500, 2601000, '2024-11-05 16:07:30', NULL, NULL, 0, NULL),
(98, '2024-11-13 18:15:00.000', NULL, 107, 110, 0, 'MYHOTEL20241112161402', NULL, NULL, 2724000, '2024-11-12 16:14:02', NULL, NULL, 1, 7),
(99, '2024-11-13 18:15:00.000', NULL, 108, 111, 0, 'MYHOTEL20241112161734', NULL, NULL, 2724000, '2024-11-12 16:17:34', NULL, NULL, 1, 7),
(100, '2024-11-13 18:15:00.000', NULL, 109, 112, 0, 'MYHOTEL20241112161738', NULL, NULL, 2724000, '2024-11-12 16:17:38', NULL, NULL, 1, 7),
(101, '2024-11-13 18:15:00.000', NULL, 110, 113, 0, 'MYHOTEL20241112161739', NULL, NULL, 2724000, '2024-11-12 16:17:39', NULL, NULL, 1, 7),
(102, '2024-11-13 18:15:00.000', NULL, 111, 114, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:40', NULL, NULL, 1, 7),
(103, '2024-11-13 18:15:00.000', NULL, 112, 115, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:40', NULL, NULL, 1, 7),
(104, '2024-11-13 18:15:00.000', NULL, 113, 116, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:40', NULL, NULL, 1, 7),
(105, '2024-11-13 18:15:00.000', NULL, 114, 117, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:40', NULL, NULL, 1, 7),
(106, '2024-11-13 18:15:00.000', NULL, 115, 118, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:40', NULL, NULL, 1, 7),
(107, '2024-11-13 18:15:00.000', NULL, 116, 119, 0, 'MYHOTEL20241112161740', NULL, NULL, 2724000, '2024-11-12 16:17:41', NULL, NULL, 1, 7),
(108, '2024-11-13 16:15:00.000', NULL, 117, 120, 0, 'MYHOTEL20241112162504', NULL, NULL, 908000, '2024-11-12 16:25:04', NULL, NULL, 1, 7),
(109, '2024-10-29 17:15:00.000', NULL, 118, 121, 0, 'MYHOTEL20241112162546', NULL, NULL, 235000, '2024-11-12 16:25:46', NULL, NULL, 1, 4),
(110, '2024-11-24 17:15:00.000', NULL, 119, 122, 0, 'MYHOTEL20241112162937', NULL, NULL, 908000, '2024-11-12 16:29:37', NULL, NULL, 1, 7),
(111, '2024-11-14 19:00:00.000', NULL, 123, 126, 0, 'MYHOTEL20241112164721', NULL, NULL, 1816000, '2024-11-12 16:47:21', NULL, NULL, 1, 7),
(112, '2024-11-24 17:15:00.000', NULL, 124, 127, 0, 'MYHOTEL20241112164730', NULL, NULL, 908000, '2024-11-12 16:47:30', NULL, NULL, 1, 7),
(113, '15-11-2024', '16-11-2024', 125, 128, -2, 'MYHOTEL8600', 'SEPNGUYEN', 497336, 3055064, '2024-11-12 16:50:59', '2024-11-13 00:41:01', NULL, 0, NULL),
(114, '13-11-2024', '15-11-2024', 126, 129, 0, 'MYHOTEL9028', 'HELLOVKU', 495900, 2114100, '2024-11-12 17:27:02', NULL, NULL, 0, NULL),
(115, '19-11-2024', '20-11-2024', 127, 130, -2, 'MYHOTEL2877', 'HELLOVKU', 247950, 1057050, '2024-11-12 17:28:31', '2024-11-12 23:58:39', NULL, 0, NULL),
(116, '19-11-2024', '20-11-2024', 128, 131, -2, 'MYHOTEL4520', 'HELLOVKU', 247950, 1057050, '2024-11-12 17:29:15', '2024-11-12 23:57:58', NULL, 0, NULL),
(117, '07-11-2024', '09-11-2024', 129, 132, 0, 'MYHOTEL7770', 'CHAODANANG', 229500, 2601000, '2024-11-12 17:31:36', '2024-11-13 00:35:03', NULL, 0, 21),
(118, '19-11-2024', '20-11-2024', 130, 133, -2, 'MYHOTEL9454', 'HELLOVKU', 247950, 1057050, '2024-11-12 17:33:17', '2024-11-13 00:35:02', NULL, 0, 21),
(119, '21-11-2024', '22-11-2024', 131, 134, 0, 'MYHOTEL9331', 'SEPNGUYEN', 214200, 1484100, '2024-11-13 00:52:18', NULL, NULL, 0, NULL),
(120, '15-11-2024', '17-11-2024', 132, 135, 0, 'MYHOTEL2397', 'CHAODANANG', 403920, 4084080, '2024-11-14 17:41:24', NULL, NULL, 0, NULL),
(121, '15-11-2024', '17-11-2024', 133, 136, 0, 'MYHOTEL3769', 'CHAODANANG', 352440, 3563560, '2024-11-14 17:42:50', NULL, NULL, 0, NULL),
(122, '15-11-2024', '17-11-2024', 134, 137, 0, 'MYHOTEL2319', 'Không có', 0, 2830500, '2024-11-14 18:21:55', NULL, NULL, 0, NULL),
(123, '18-11-2024', '20-11-2024', 135, 138, 2, 'MYHOTEL3100', 'CHAODANANG', 145799.8542, 1652398, '2024-11-15 04:25:43', NULL, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_orderer`
--

CREATE TABLE `tbl_orderer` (
  `orderer_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `orderer_name` varchar(256) DEFAULT NULL,
  `orderer_phone` varchar(256) DEFAULT NULL,
  `orderer_email` varchar(256) DEFAULT NULL,
  `orderer_type_bed` int(11) DEFAULT NULL,
  `orderer_special_requirements` int(11) DEFAULT NULL,
  `orderer_own_require` varchar(256) DEFAULT NULL,
  `orderer_bill_require` int(11) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_orderer`
--

INSERT INTO `tbl_orderer` (`orderer_id`, `customer_id`, `orderer_name`, `orderer_phone`, `orderer_email`, `orderer_type_bed`, `orderer_special_requirements`, `orderer_own_require`, `orderer_bill_require`, `created_at`, `updated_at`) VALUES
(31, 15, 'Nguyễn Văn Vĩnh Nguyên', '839519415', 'nguyenvy1470@gmail.com', 1, 1, 'Không Có', 1, '2024-05-05 12:56:02', NULL),
(32, 15, 'Nguyễn Văn Vĩnh Nguyên', '839519415', 'nguyenvy1470@gmail.com', 1, 2, 'Không Có', 1, '2024-05-05 13:13:33', NULL),
(33, 3, 'Nhân', '987654321', 'nhanlk.21it@vku.udn.vn', 1, 0, 'Không Có', 1, '2024-05-06 08:33:38', NULL),
(34, 3, 'Nhân', '987654321', 'nhanlk.21it@vku.udn.vn', 2, 3, 'Không Có', 1, '2024-05-06 10:05:11', NULL),
(51, 15, 'Nguyễn Văn Vĩnh Nguyên', '839519415', 'nguyenvy1470@gmail.com', 2, 0, 'Không có', 1, '2024-05-21 17:03:33', NULL),
(52, 17, 'Nguyên Vĩnh', '839519415', 'nguyennvv.21it@vku.udn.vn', 1, 0, 'Không có', 1, '2024-06-04 11:33:55', NULL),
(57, 17, 'Nguyên Vĩnh', '839519415', 'nguyennvv.21it@vku.udn.vn', 1, 0, 'Không có', 1, '2024-06-04 12:11:19', NULL),
(58, 15, 'Nguyễn Văn Vĩnh Nguyên', '839519415', 'nguyenvy1470@gmail.com', 2, 3, 'Không Có', 1, '2024-06-04 12:41:11', NULL),
(59, 15, 'Nguyễn Văn Vĩnh Nguyên', '839519415', 'nguyenvy1470@gmail.com', 1, 3, 'Không Có', 1, '2024-06-04 12:54:36', NULL),
(60, 3, 'Nhân Kha Le', '987654321', 'nhanlk.21it@vku.udn.vn', 2, 0, 'Không có', 1, '2024-10-05 03:41:28', NULL),
(61, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:11:01', '2024-10-29 17:32:44'),
(62, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:11:28', '2024-10-29 17:32:46'),
(63, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:12:04', '2024-10-29 17:32:48'),
(64, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:12:41', '2024-10-29 17:32:49'),
(65, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:13:02', '2024-10-29 17:32:51'),
(66, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:48:34', '2024-10-29 17:32:54'),
(67, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:48:53', '2024-10-29 17:32:57'),
(68, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:49:47', '2024-10-29 17:32:59'),
(69, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 15:56:20', '2024-10-29 17:33:04'),
(70, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:00:41', '2024-10-29 17:33:06'),
(71, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:02:38', '2024-10-29 17:32:41'),
(72, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:03:00', '2024-10-29 17:32:38'),
(73, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:03:36', '2024-10-29 17:32:27'),
(74, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:03:50', '2024-10-29 17:32:26'),
(75, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:16:03', '2024-10-29 17:32:21'),
(76, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:17:01', '2024-10-29 17:32:20'),
(77, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:17:35', '2024-10-29 17:32:17'),
(78, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:19:57', '2024-10-29 17:32:15'),
(79, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:20:20', '2024-10-29 17:32:14'),
(80, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:20:52', '2024-10-29 17:32:11'),
(81, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:21:09', '2024-10-29 17:32:09'),
(82, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:23:39', '2024-10-29 17:32:07'),
(83, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:27:08', '2024-10-29 17:32:05'),
(84, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:28:15', '2024-10-29 17:32:03'),
(85, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:28:35', '2024-10-29 17:31:59'),
(86, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:29:29', '2024-10-29 17:31:55'),
(87, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:30:31', '2024-10-29 17:31:53'),
(88, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:30:31', '2024-10-29 17:31:51'),
(89, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:30:54', '2024-10-29 17:31:48'),
(90, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:31:38', '2024-10-29 17:31:46'),
(91, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:32:34', '2024-10-29 17:31:43'),
(92, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:34:03', '2024-10-29 17:31:39'),
(93, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:34:12', '2024-10-29 17:31:37'),
(94, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:34:34', '2024-10-29 17:31:34'),
(95, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 16:37:14', '2024-10-29 17:31:30'),
(96, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 17:52:33', '2024-10-29 17:31:28'),
(97, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-10-28 17:53:44', '2024-10-29 17:30:01'),
(98, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 2, 0, '5 star', 1, '2024-11-05 15:59:26', NULL),
(99, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:00:40', NULL),
(100, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:02:03', NULL),
(101, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:02:57', NULL),
(102, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:05:01', NULL),
(103, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:06:09', NULL),
(104, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:06:27', NULL),
(105, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:06:40', NULL),
(106, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-05 16:07:30', NULL),
(107, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-11-12 16:14:02', NULL),
(108, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:34', NULL),
(109, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:38', NULL),
(110, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:39', NULL),
(111, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:40', NULL),
(112, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:40', NULL),
(113, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:40', NULL),
(114, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:40', NULL),
(115, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:40', NULL),
(116, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'tuyet voi', 1, '2024-11-12 16:17:41', NULL),
(117, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'aaa', 1, '2024-11-12 16:25:04', NULL),
(118, NULL, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'Không có', 1, '2024-11-12 16:25:46', NULL),
(119, NULL, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'aaa', 1, '2024-11-12 16:29:37', NULL),
(120, NULL, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'aaaa', 1, '2024-11-12 16:36:39', NULL),
(121, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'aaaa', 1, '2024-11-12 16:38:54', NULL),
(122, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'aaa', 1, '2024-11-12 16:39:10', NULL),
(123, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, NULL, 'aaaa', 1, '2024-11-12 16:47:21', NULL),
(124, 15, 'Nguyễn Văn Vĩnh Nguyen', NULL, 'nguyenvy1470@gmail.com', 1, NULL, 'aaa', 1, '2024-11-12 16:47:30', NULL),
(125, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 2, 0, 'Không có', 1, '2024-11-12 16:50:59', NULL),
(126, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-12 17:27:02', NULL),
(127, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-12 17:28:31', NULL),
(128, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-12 17:29:15', NULL),
(129, 5, 'Nhân', '987654321', 'nhan@vku.udn.vn\r\n', 3, 0, 'Không có', 1, '2024-11-12 17:31:36', NULL),
(130, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-12 17:33:17', NULL),
(131, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-13 00:52:18', NULL),
(132, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-14 17:41:24', NULL),
(133, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 1, 0, 'Không có', 1, '2024-11-14 17:42:50', NULL),
(134, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 3, 0, 'Không có', 1, '2024-11-14 18:21:55', NULL),
(135, 15, 'Nguyễn Văn Vĩnh Nguyen', '839519415', 'nguyenvy1470@gmail.com', 2, 0, 'Không có', 1, '2024-11-15 04:25:43', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_order_details`
--

CREATE TABLE `tbl_order_details` (
  `order_details_id` int(11) NOT NULL,
  `order_code` varchar(256) NOT NULL,
  `hotel_id` int(11) NOT NULL,
  `hotel_name` varchar(256) NOT NULL,
  `room_id` int(11) NOT NULL,
  `room_name` varchar(256) NOT NULL,
  `type_room_id` int(11) NOT NULL,
  `price_room` double NOT NULL,
  `hotel_fee` double NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_order_details`
--

INSERT INTO `tbl_order_details` (`order_details_id`, `order_code`, `hotel_id`, `hotel_name`, `room_id`, `room_name`, `type_room_id`, `price_room`, `hotel_fee`, `created_at`, `updated_at`) VALUES
(31, 'MYHOTEL2607', 3, 'Mường Thanh Luxury', 5, 'Phòng Premier Deluxe Twin', 3, 1500000, 100000, '2024-05-05 12:56:02', NULL),
(32, 'MYHOTEL2538', 2, 'Meliá Vinpearl Riverfront', 6, 'Deluxe Room', 7, 2350144.8, 235014.48, '2024-05-05 13:13:33', NULL),
(33, 'MYHOTEL7530', 20, 'Khách Sạn Eden Ocean View', 59, 'Premium Sea Side Twin', 154, 7833816, 0, '2024-05-06 08:33:38', NULL),
(34, 'MYHOTEL432', 19, 'The Blossom Resort Island', 56, 'Deluxe King Room with Street View', 147, 4150000, 0, '2024-05-06 10:05:11', NULL),
(51, 'MYHOTEL8735', 3, 'Mường Thanh Luxury', 2, 'Phòng Grand Suite', 1, 2418680, 100000, '2024-05-21 17:03:33', NULL),
(52, 'MYHOTEL9671', 5, 'The Nalod', 13, 'Phòng Premier Deluxe Twin', 29, 4419295.2, 100000, '2024-06-04 11:33:55', '2024-06-16 15:35:56'),
(57, 'MYHOTEL8696', 5, 'The Nalod', 12, 'Phòng Deluxe King', 26, 2616960, 100000, '2024-06-04 12:11:19', '2024-06-16 15:36:08'),
(58, 'MYHOTEL9000', 19, 'The Blossom Resort Island', 56, 'Deluxe King Room with Street View', 147, 2075000, 0, '2024-06-04 12:41:11', NULL),
(59, 'MYHOTEL2930', 3, 'Mường Thanh Luxury', 5, 'Phòng Premier Deluxe Twin', 3, 7500000, 100000, '2024-06-04 12:54:36', NULL),
(60, 'MYHOTEL9254', 15, 'Four Points by Sheraton', 42, 'Superior King Ocean View', 110, 6137877.2, 0, '2024-10-05 03:41:28', NULL),
(61, 'MYHOTEL7890', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 18, 1798198.2018, 178199.8218, '2024-11-05 15:59:26', NULL),
(62, 'MYHOTEL3596', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:00:40', NULL),
(63, 'MYHOTEL3023', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:02:03', NULL),
(64, 'MYHOTEL7770', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:02:57', NULL),
(65, 'MYHOTEL7770', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:05:01', NULL),
(66, 'MYHOTEL7770', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:06:09', NULL),
(67, 'MYHOTEL7770', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:06:27', NULL),
(68, 'MYHOTEL6507', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:06:40', NULL),
(69, 'MYHOTEL2476', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-05 16:07:30', NULL),
(70, 'MYHOTEL8600', 10, 'Le Sands Oceanfront', 29, 'Premier Oceanfront Twin, Trực Diện Biển, Tầng cao, Ban Công', 79, 3055064, 0, '2024-11-12 16:50:59', NULL),
(71, 'MYHOTEL9028', 21, 'Risemount Premier Resort ', 62, 'Superior Twin Room', 161, 2114100, 0, '2024-11-12 17:27:02', NULL),
(72, 'MYHOTEL2877', 21, 'Risemount Premier Resort ', 62, 'Superior Twin Room', 161, 1057050, 0, '2024-11-12 17:28:31', NULL),
(73, 'MYHOTEL4520', 21, 'Risemount Premier Resort ', 62, 'Superior Twin Room', 161, 1057050, 0, '2024-11-12 17:29:15', NULL),
(74, 'MYHOTEL7770', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2601000, 280500, '2024-11-12 17:31:36', NULL),
(75, 'MYHOTEL9454', 21, 'Risemount Premier Resort ', 62, 'Superior Twin Room', 161, 1057050, 0, '2024-11-12 17:33:17', NULL),
(76, 'MYHOTEL9331', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 17, 1484100, 168300, '2024-11-13 00:52:18', NULL),
(77, 'MYHOTEL2397', 10, 'Le Sands Oceanfront', 27, 'Deluxe Ocean Twin, Ban Công, Hướng Biển', 75, 4084080, 0, '2024-11-14 17:41:24', NULL),
(78, 'MYHOTEL3769', 21, 'Risemount Premier Resort ', 60, 'Superior King Room', 156, 3563560, 0, '2024-11-14 17:42:50', NULL),
(79, 'MYHOTEL2319', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 19, 2830500, 280500, '2024-11-14 18:21:55', NULL),
(80, 'MYHOTEL3100', 4, 'Sheraton Grand Resort', 9, 'Phòng Deluxe King', 18, 1652398.3476, 178199.8218, '2024-11-15 04:25:43', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_order_details_restaurant`
--

CREATE TABLE `tbl_order_details_restaurant` (
  `order_details_id` int(11) NOT NULL,
  `order_code` varchar(256) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `restaurant_menu_id` int(11) NOT NULL,
  `restaurant_menu_price` int(11) NOT NULL,
  `restaurant_menu_quantity` int(11) NOT NULL,
  `table_restaurant_price` double DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_order_details_restaurant`
--

INSERT INTO `tbl_order_details_restaurant` (`order_details_id`, `order_code`, `restaurant_id`, `restaurant_menu_id`, `restaurant_menu_price`, `restaurant_menu_quantity`, `table_restaurant_price`, `created_at`, `updated_at`) VALUES
(1, 'MYHOTEL+20241028151022', 4, 12, 60000, 1, NULL, '2024-10-28 15:10:22', '2024-10-28 15:10:22'),
(2, 'MYHOTEL+20241028151022', 4, 13, 90000, 1, NULL, '2024-10-28 15:10:22', '2024-10-28 15:10:22'),
(3, 'MYHOTEL+20241028151022', 4, 14, 85000, 1, NULL, '2024-10-28 15:10:22', '2024-10-28 15:10:22'),
(4, 'MYHOTEL+20241028151101', 4, 12, 60000, 1, NULL, '2024-10-28 15:11:01', '2024-10-28 15:11:01'),
(5, 'MYHOTEL+20241028151101', 4, 13, 90000, 1, NULL, '2024-10-28 15:11:01', '2024-10-28 15:11:01'),
(6, 'MYHOTEL+20241028151101', 4, 14, 85000, 1, NULL, '2024-10-28 15:11:01', '2024-10-28 15:11:01'),
(7, 'MYHOTEL+20241028151128', 4, 12, 60000, 1, NULL, '2024-10-28 15:11:28', '2024-10-28 15:11:28'),
(8, 'MYHOTEL+20241028151128', 4, 13, 90000, 1, NULL, '2024-10-28 15:11:28', '2024-10-28 15:11:28'),
(9, 'MYHOTEL+20241028151128', 4, 14, 85000, 1, NULL, '2024-10-28 15:11:28', '2024-10-28 15:11:28'),
(10, 'MYHOTEL+20241028151204', 4, 12, 60000, 1, NULL, '2024-10-28 15:12:04', '2024-10-28 15:12:04'),
(11, 'MYHOTEL+20241028151204', 4, 13, 90000, 1, NULL, '2024-10-28 15:12:04', '2024-10-28 15:12:04'),
(12, 'MYHOTEL+20241028151204', 4, 14, 85000, 1, NULL, '2024-10-28 15:12:04', '2024-10-28 15:12:04'),
(13, 'MYHOTEL+20241028151241', 4, 12, 60000, 1, NULL, '2024-10-28 15:12:41', '2024-10-28 15:12:41'),
(14, 'MYHOTEL+20241028151241', 4, 13, 90000, 1, NULL, '2024-10-28 15:12:41', '2024-10-28 15:12:41'),
(15, 'MYHOTEL+20241028151241', 4, 14, 85000, 1, NULL, '2024-10-28 15:12:41', '2024-10-28 15:12:41'),
(16, 'MYHOTEL20241028151302', 4, 12, 60000, 1, NULL, '2024-10-28 15:13:02', '2024-10-28 15:13:02'),
(17, 'MYHOTEL20241028151302', 4, 13, 90000, 1, NULL, '2024-10-28 15:13:02', '2024-10-28 15:13:02'),
(18, 'MYHOTEL20241028151302', 4, 14, 85000, 1, NULL, '2024-10-28 15:13:02', '2024-10-28 15:13:02'),
(19, 'MYHOTEL20241028154834', 4, 12, 60000, 1, NULL, '2024-10-28 15:48:34', '2024-10-28 15:48:34'),
(20, 'MYHOTEL20241028154834', 4, 13, 90000, 1, NULL, '2024-10-28 15:48:34', '2024-10-28 15:48:34'),
(21, 'MYHOTEL20241028154834', 4, 15, 130000, 1, NULL, '2024-10-28 15:48:34', '2024-10-28 15:48:34'),
(22, 'MYHOTEL20241028154834', 4, 16, 60000, 1, NULL, '2024-10-28 15:48:34', '2024-10-28 15:48:34'),
(23, 'MYHOTEL20241028154853', 4, 12, 60000, 1, NULL, '2024-10-28 15:48:53', '2024-10-28 15:48:53'),
(24, 'MYHOTEL20241028154853', 4, 13, 90000, 1, NULL, '2024-10-28 15:48:53', '2024-10-28 15:48:53'),
(25, 'MYHOTEL20241028154853', 4, 15, 130000, 1, NULL, '2024-10-28 15:48:53', '2024-10-28 15:48:53'),
(26, 'MYHOTEL20241028154853', 4, 16, 60000, 1, NULL, '2024-10-28 15:48:53', '2024-10-28 15:48:53'),
(27, 'MYHOTEL20241028154947', 4, 12, 60000, 1, NULL, '2024-10-28 15:49:47', '2024-10-28 15:49:47'),
(28, 'MYHOTEL20241028154947', 4, 13, 90000, 1, NULL, '2024-10-28 15:49:47', '2024-10-28 15:49:47'),
(29, 'MYHOTEL20241028154947', 4, 15, 130000, 1, NULL, '2024-10-28 15:49:47', '2024-10-28 15:49:47'),
(30, 'MYHOTEL20241028154947', 4, 16, 60000, 1, NULL, '2024-10-28 15:49:47', '2024-10-28 15:49:47'),
(31, 'MYHOTEL20241028155620', 4, 12, 60000, 1, NULL, '2024-10-28 15:56:20', '2024-10-28 15:56:20'),
(32, 'MYHOTEL20241028155620', 4, 13, 90000, 1, NULL, '2024-10-28 15:56:20', '2024-10-28 15:56:20'),
(33, 'MYHOTEL20241028155620', 4, 15, 130000, 1, NULL, '2024-10-28 15:56:20', '2024-10-28 15:56:20'),
(34, 'MYHOTEL20241028155620', 4, 16, 60000, 1, NULL, '2024-10-28 15:56:20', '2024-10-28 15:56:20'),
(35, 'MYHOTEL20241028160041', 4, 12, 60000, 1, NULL, '2024-10-28 16:00:41', '2024-10-28 16:00:41'),
(36, 'MYHOTEL20241028160041', 4, 13, 90000, 1, NULL, '2024-10-28 16:00:41', '2024-10-28 16:00:41'),
(37, 'MYHOTEL20241028160041', 4, 15, 130000, 1, NULL, '2024-10-28 16:00:41', '2024-10-28 16:00:41'),
(38, 'MYHOTEL20241028160041', 4, 16, 60000, 1, NULL, '2024-10-28 16:00:41', '2024-10-28 16:00:41'),
(39, 'MYHOTEL20241028160238', 4, 12, 60000, 1, NULL, '2024-10-28 16:02:38', '2024-10-28 16:02:38'),
(40, 'MYHOTEL20241028160238', 4, 13, 90000, 1, NULL, '2024-10-28 16:02:38', '2024-10-28 16:02:38'),
(41, 'MYHOTEL20241028160238', 4, 15, 130000, 1, NULL, '2024-10-28 16:02:38', '2024-10-28 16:02:38'),
(42, 'MYHOTEL20241028160238', 4, 16, 60000, 1, NULL, '2024-10-28 16:02:38', '2024-10-28 16:02:38'),
(43, 'MYHOTEL20241028160300', 4, 12, 60000, 1, NULL, '2024-10-28 16:03:00', '2024-10-28 16:03:00'),
(44, 'MYHOTEL20241028160300', 4, 13, 90000, 1, NULL, '2024-10-28 16:03:00', '2024-10-28 16:03:00'),
(45, 'MYHOTEL20241028160300', 4, 15, 130000, 1, NULL, '2024-10-28 16:03:00', '2024-10-28 16:03:00'),
(46, 'MYHOTEL20241028160300', 4, 16, 60000, 1, NULL, '2024-10-28 16:03:00', '2024-10-28 16:03:00'),
(47, 'MYHOTEL20241028160336', 4, 12, 60000, 1, NULL, '2024-10-28 16:03:36', '2024-10-28 16:03:36'),
(48, 'MYHOTEL20241028160336', 4, 13, 90000, 1, NULL, '2024-10-28 16:03:36', '2024-10-28 16:03:36'),
(49, 'MYHOTEL20241028160336', 4, 15, 130000, 1, NULL, '2024-10-28 16:03:36', '2024-10-28 16:03:36'),
(50, 'MYHOTEL20241028160336', 4, 16, 60000, 1, NULL, '2024-10-28 16:03:36', '2024-10-28 16:03:36'),
(51, 'MYHOTEL20241028160349', 4, 12, 60000, 1, NULL, '2024-10-28 16:03:49', '2024-10-28 16:03:49'),
(52, 'MYHOTEL20241028160349', 4, 13, 90000, 1, NULL, '2024-10-28 16:03:49', '2024-10-28 16:03:49'),
(53, 'MYHOTEL20241028160349', 4, 15, 130000, 1, NULL, '2024-10-28 16:03:49', '2024-10-28 16:03:49'),
(54, 'MYHOTEL20241028160349', 4, 16, 60000, 1, NULL, '2024-10-28 16:03:49', '2024-10-28 16:03:49'),
(55, 'MYHOTEL20241028161603', 4, 12, 180000, 3, NULL, '2024-10-28 16:16:03', '2024-10-28 16:16:03'),
(56, 'MYHOTEL20241028161603', 4, 15, 390000, 3, NULL, '2024-10-28 16:16:03', '2024-10-28 16:16:03'),
(57, 'MYHOTEL20241028161701', 4, 12, 180000, 3, NULL, '2024-10-28 16:17:01', '2024-10-28 16:17:01'),
(58, 'MYHOTEL20241028161701', 4, 15, 390000, 3, NULL, '2024-10-28 16:17:01', '2024-10-28 16:17:01'),
(59, 'MYHOTEL20241028161735', 4, 12, 180000, 3, NULL, '2024-10-28 16:17:35', '2024-10-28 16:17:35'),
(60, 'MYHOTEL20241028161735', 4, 15, 390000, 3, NULL, '2024-10-28 16:17:35', '2024-10-28 16:17:35'),
(61, 'MYHOTEL20241028161957', 4, 12, 180000, 3, NULL, '2024-10-28 16:19:57', '2024-10-28 16:19:57'),
(62, 'MYHOTEL20241028161957', 4, 15, 390000, 3, NULL, '2024-10-28 16:19:57', '2024-10-28 16:19:57'),
(63, 'MYHOTEL20241028162020', 4, 12, 180000, 3, NULL, '2024-10-28 16:20:20', '2024-10-28 16:20:20'),
(64, 'MYHOTEL20241028162020', 4, 15, 390000, 3, NULL, '2024-10-28 16:20:20', '2024-10-28 16:20:20'),
(65, 'MYHOTEL20241028162052', 4, 12, 180000, 3, NULL, '2024-10-28 16:20:52', '2024-10-28 16:20:52'),
(66, 'MYHOTEL20241028162052', 4, 15, 390000, 3, NULL, '2024-10-28 16:20:52', '2024-10-28 16:20:52'),
(67, 'MYHOTEL20241028162109', 4, 12, 180000, 3, NULL, '2024-10-28 16:21:09', '2024-10-28 16:21:09'),
(68, 'MYHOTEL20241028162109', 4, 15, 390000, 3, NULL, '2024-10-28 16:21:09', '2024-10-28 16:21:09'),
(69, 'MYHOTEL20241028162339', 4, 12, 60000, 1, NULL, '2024-10-28 16:23:39', '2024-10-28 16:23:39'),
(70, 'MYHOTEL20241028162339', 4, 13, 90000, 1, NULL, '2024-10-28 16:23:39', '2024-10-28 16:23:39'),
(71, 'MYHOTEL20241028162339', 4, 14, 85000, 1, NULL, '2024-10-28 16:23:39', '2024-10-28 16:23:39'),
(72, 'MYHOTEL20241028162708', 4, 12, 60000, 1, NULL, '2024-10-28 16:27:08', '2024-10-28 16:27:08'),
(73, 'MYHOTEL20241028162708', 4, 13, 90000, 1, NULL, '2024-10-28 16:27:08', '2024-10-28 16:27:08'),
(74, 'MYHOTEL20241028162708', 4, 14, 85000, 1, NULL, '2024-10-28 16:27:08', '2024-10-28 16:27:08'),
(75, 'MYHOTEL20241028162815', 4, 12, 60000, 1, NULL, '2024-10-28 16:28:15', '2024-10-28 16:28:15'),
(76, 'MYHOTEL20241028162815', 4, 13, 90000, 1, NULL, '2024-10-28 16:28:15', '2024-10-28 16:28:15'),
(77, 'MYHOTEL20241028162815', 4, 14, 85000, 1, NULL, '2024-10-28 16:28:15', '2024-10-28 16:28:15'),
(78, 'MYHOTEL20241028162834', 4, 12, 60000, 1, NULL, '2024-10-28 16:28:35', '2024-10-28 16:28:35'),
(79, 'MYHOTEL20241028162834', 4, 13, 90000, 1, NULL, '2024-10-28 16:28:35', '2024-10-28 16:28:35'),
(80, 'MYHOTEL20241028162834', 4, 14, 85000, 1, NULL, '2024-10-28 16:28:35', '2024-10-28 16:28:35'),
(81, 'MYHOTEL20241028162929', 4, 12, 60000, 1, NULL, '2024-10-28 16:29:29', '2024-10-28 16:29:29'),
(82, 'MYHOTEL20241028162929', 4, 13, 90000, 1, NULL, '2024-10-28 16:29:29', '2024-10-28 16:29:29'),
(83, 'MYHOTEL20241028162929', 4, 14, 85000, 1, NULL, '2024-10-28 16:29:29', '2024-10-28 16:29:29'),
(84, 'MYHOTEL20241028163031', 4, 12, 60000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(85, 'MYHOTEL20241028163031', 4, 13, 90000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(86, 'MYHOTEL20241028163031', 4, 14, 85000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(87, 'MYHOTEL20241028163031', 4, 12, 60000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(88, 'MYHOTEL20241028163031', 4, 13, 90000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(89, 'MYHOTEL20241028163031', 4, 14, 85000, 1, NULL, '2024-10-28 16:30:31', '2024-10-28 16:30:31'),
(90, 'MYHOTEL20241028163053', 4, 12, 60000, 1, NULL, '2024-10-28 16:30:54', '2024-10-28 16:30:54'),
(91, 'MYHOTEL20241028163053', 4, 13, 90000, 1, NULL, '2024-10-28 16:30:54', '2024-10-28 16:30:54'),
(92, 'MYHOTEL20241028163053', 4, 14, 85000, 1, NULL, '2024-10-28 16:30:54', '2024-10-28 16:30:54'),
(93, 'MYHOTEL20241028163138', 4, 12, 60000, 1, NULL, '2024-10-28 16:31:38', '2024-10-28 16:31:38'),
(94, 'MYHOTEL20241028163138', 4, 13, 90000, 1, NULL, '2024-10-28 16:31:38', '2024-10-28 16:31:38'),
(95, 'MYHOTEL20241028163138', 4, 14, 85000, 1, NULL, '2024-10-28 16:31:38', '2024-10-28 16:31:38'),
(96, 'MYHOTEL20241028163234', 4, 12, 60000, 1, NULL, '2024-10-28 16:32:34', '2024-10-28 16:32:34'),
(97, 'MYHOTEL20241028163234', 4, 13, 90000, 1, NULL, '2024-10-28 16:32:34', '2024-10-28 16:32:34'),
(98, 'MYHOTEL20241028163234', 4, 14, 85000, 1, NULL, '2024-10-28 16:32:34', '2024-10-28 16:32:34'),
(99, 'MYHOTEL20241028163403', 4, 12, 60000, 1, NULL, '2024-10-28 16:34:03', '2024-10-28 16:34:03'),
(100, 'MYHOTEL20241028163403', 4, 13, 90000, 1, NULL, '2024-10-28 16:34:03', '2024-10-28 16:34:03'),
(101, 'MYHOTEL20241028163403', 4, 14, 85000, 1, NULL, '2024-10-28 16:34:03', '2024-10-28 16:34:03'),
(102, 'MYHOTEL20241028163412', 4, 12, 60000, 1, NULL, '2024-10-28 16:34:12', '2024-10-28 16:34:12'),
(103, 'MYHOTEL20241028163412', 4, 13, 90000, 1, NULL, '2024-10-28 16:34:12', '2024-10-28 16:34:12'),
(104, 'MYHOTEL20241028163412', 4, 14, 85000, 1, NULL, '2024-10-28 16:34:12', '2024-10-28 16:34:12'),
(105, 'MYHOTEL20241028163434', 4, 12, 60000, 1, NULL, '2024-10-28 16:34:34', '2024-10-28 16:34:34'),
(106, 'MYHOTEL20241028163434', 4, 13, 90000, 1, NULL, '2024-10-28 16:34:34', '2024-10-28 16:34:34'),
(107, 'MYHOTEL20241028163434', 4, 14, 85000, 1, NULL, '2024-10-28 16:34:34', '2024-10-28 16:34:34'),
(108, 'MYHOTEL20241028163714', 4, 12, 60000, 1, NULL, '2024-10-28 16:37:14', '2024-10-28 16:37:14'),
(109, 'MYHOTEL20241028163714', 4, 13, 90000, 1, NULL, '2024-10-28 16:37:14', '2024-10-28 16:37:14'),
(110, 'MYHOTEL20241028163714', 4, 14, 85000, 1, NULL, '2024-10-28 16:37:14', '2024-10-28 16:37:14'),
(111, 'MYHOTEL20241028175233', 4, 12, 60000, 1, NULL, '2024-10-28 17:52:33', '2024-10-28 17:52:33'),
(112, 'MYHOTEL20241028175233', 4, 13, 90000, 1, NULL, '2024-10-28 17:52:33', '2024-10-28 17:52:33'),
(113, 'MYHOTEL20241028175233', 4, 14, 85000, 1, NULL, '2024-10-28 17:52:33', '2024-10-28 17:52:33'),
(114, 'MYHOTEL20241028175233', 4, 15, 130000, 1, NULL, '2024-10-28 17:52:33', '2024-10-28 17:52:33'),
(115, 'MYHOTEL20241028175344', 4, 12, 60000, 1, NULL, '2024-10-28 17:53:44', '2024-10-28 17:53:44'),
(116, 'MYHOTEL20241028175344', 4, 13, 90000, 1, NULL, '2024-10-28 17:53:44', '2024-10-28 17:53:44'),
(117, 'MYHOTEL20241028175344', 4, 14, 85000, 1, NULL, '2024-10-28 17:53:44', '2024-10-28 17:53:44'),
(118, 'MYHOTEL20241112161402', 7, 34, 1827000, 3, NULL, '2024-11-12 16:14:02', '2024-11-12 16:14:02'),
(119, 'MYHOTEL20241112161402', 7, 35, 897000, 3, NULL, '2024-11-12 16:14:02', '2024-11-12 16:14:02'),
(120, 'MYHOTEL20241112161734', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:34', '2024-11-12 16:17:34'),
(121, 'MYHOTEL20241112161734', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:34', '2024-11-12 16:17:34'),
(122, 'MYHOTEL20241112161738', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:38', '2024-11-12 16:17:38'),
(123, 'MYHOTEL20241112161738', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:38', '2024-11-12 16:17:38'),
(124, 'MYHOTEL20241112161739', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:39', '2024-11-12 16:17:39'),
(125, 'MYHOTEL20241112161739', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:39', '2024-11-12 16:17:39'),
(126, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(127, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(128, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(129, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(130, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(131, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(132, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(133, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(134, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(135, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:40', '2024-11-12 16:17:40'),
(136, 'MYHOTEL20241112161740', 7, 34, 1827000, 3, NULL, '2024-11-12 16:17:41', '2024-11-12 16:17:41'),
(137, 'MYHOTEL20241112161740', 7, 35, 897000, 3, NULL, '2024-11-12 16:17:41', '2024-11-12 16:17:41'),
(138, 'MYHOTEL20241112162504', 7, 34, 609000, 1, NULL, '2024-11-12 16:25:04', '2024-11-12 16:25:04'),
(139, 'MYHOTEL20241112162504', 7, 35, 299000, 1, NULL, '2024-11-12 16:25:04', '2024-11-12 16:25:04'),
(140, 'MYHOTEL20241112162546', 4, 12, 60000, 1, NULL, '2024-11-12 16:25:46', '2024-11-12 16:25:46'),
(141, 'MYHOTEL20241112162546', 4, 13, 90000, 1, NULL, '2024-11-12 16:25:46', '2024-11-12 16:25:46'),
(142, 'MYHOTEL20241112162546', 4, 14, 85000, 1, NULL, '2024-11-12 16:25:46', '2024-11-12 16:25:46'),
(143, 'MYHOTEL20241112162937', 7, 35, 299000, 1, NULL, '2024-11-12 16:29:37', '2024-11-12 16:29:37'),
(144, 'MYHOTEL20241112162937', 7, 34, 609000, 1, NULL, '2024-11-12 16:29:37', '2024-11-12 16:29:37'),
(145, 'MYHOTEL20241112163639', 7, 34, 1218000, 2, NULL, '2024-11-12 16:36:39', '2024-11-12 16:36:39'),
(146, 'MYHOTEL20241112163639', 7, 35, 598000, 2, NULL, '2024-11-12 16:36:39', '2024-11-12 16:36:39'),
(147, 'MYHOTEL20241112163854', 7, 34, 1218000, 2, NULL, '2024-11-12 16:38:54', '2024-11-12 16:38:54'),
(148, 'MYHOTEL20241112163854', 7, 35, 598000, 2, NULL, '2024-11-12 16:38:54', '2024-11-12 16:38:54'),
(149, 'MYHOTEL20241112163910', 7, 35, 299000, 1, NULL, '2024-11-12 16:39:10', '2024-11-12 16:39:10'),
(150, 'MYHOTEL20241112163910', 7, 34, 609000, 1, NULL, '2024-11-12 16:39:10', '2024-11-12 16:39:10'),
(151, 'MYHOTEL20241112164721', 7, 34, 1218000, 2, NULL, '2024-11-12 16:47:21', '2024-11-12 16:47:21'),
(152, 'MYHOTEL20241112164721', 7, 35, 598000, 2, NULL, '2024-11-12 16:47:21', '2024-11-12 16:47:21'),
(153, 'MYHOTEL20241112164730', 7, 35, 299000, 1, NULL, '2024-11-12 16:47:30', '2024-11-12 16:47:30'),
(154, 'MYHOTEL20241112164730', 7, 34, 609000, 1, NULL, '2024-11-12 16:47:30', '2024-11-12 16:47:30');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_payment`
--

CREATE TABLE `tbl_payment` (
  `payment_id` int(11) NOT NULL,
  `payment_method` int(11) NOT NULL,
  `payment_status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_payment`
--

INSERT INTO `tbl_payment` (`payment_id`, `payment_method`, `payment_status`) VALUES
(33, 4, 1),
(34, 4, 0),
(35, 4, 1),
(36, 4, 0),
(53, 4, 0),
(54, 4, 0),
(59, 4, 0),
(60, 1, 1),
(61, 1, 1),
(62, 4, 0),
(63, 4, 0),
(64, 4, 0),
(65, 4, 0),
(66, 4, 0),
(67, 4, 0),
(68, 4, 0),
(69, 4, 0),
(70, 4, 0),
(71, 4, 0),
(72, 4, 0),
(73, 4, 0),
(74, 4, 0),
(75, 4, 0),
(76, 4, 0),
(77, 4, 0),
(78, 4, 0),
(79, 4, 0),
(80, 4, 0),
(81, 4, 0),
(82, 4, 0),
(83, 4, 0),
(84, 4, 0),
(85, 4, 0),
(86, 4, 0),
(87, 4, 0),
(88, 4, 0),
(89, 4, 0),
(90, 4, 1),
(91, 4, 0),
(92, 4, 0),
(93, 4, 0),
(94, 4, 0),
(95, 4, 0),
(96, 4, 0),
(97, 4, 0),
(98, 4, 0),
(99, 4, 0),
(100, 4, 0),
(101, 4, 0),
(102, 4, 0),
(103, 4, 0),
(104, 4, 0),
(105, 4, 0),
(106, 4, 0),
(107, 4, 0),
(108, 4, 0),
(109, 4, 0),
(110, 4, 0),
(111, 4, 0),
(112, 4, 0),
(113, 4, 0),
(114, 4, 0),
(115, 4, 0),
(116, 4, 0),
(117, 4, 0),
(118, 4, 0),
(119, 4, 0),
(120, 4, 0),
(121, 4, 0),
(122, 4, 0),
(123, 4, 0),
(124, 4, 0),
(125, 4, 0),
(126, 4, 0),
(127, 4, 0),
(128, 4, 0),
(129, 4, 0),
(130, 4, 0),
(131, 4, 0),
(132, 4, 0),
(133, 4, 0),
(134, 4, 0),
(135, 4, 0),
(136, 4, 0),
(137, 4, 0),
(138, 4, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_restaurant`
--

CREATE TABLE `tbl_restaurant` (
  `restaurant_id` int(11) NOT NULL,
  `restaurant_name` varchar(255) NOT NULL,
  `restaurant_rank` int(1) NOT NULL,
  `restaurant_placedetails` varchar(256) NOT NULL,
  `restaurant_linkplace` varchar(255) NOT NULL,
  `restaurant_image` varchar(256) DEFAULT NULL,
  `area_id` int(1) DEFAULT NULL,
  `restaurant_desc` varchar(256) DEFAULT NULL,
  `restaurant_status` int(1) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_restaurant`
--

INSERT INTO `tbl_restaurant` (`restaurant_id`, `restaurant_name`, `restaurant_rank`, `restaurant_placedetails`, `restaurant_linkplace`, `restaurant_image`, `area_id`, `restaurant_desc`, `restaurant_status`, `created_at`, `updated_at`) VALUES
(1, 'NHÀ BẾP CHỢ HÀN', 5, '22 Hùng Vương, Hải Châu 1, Hải Châu, Đà Nẵng 550000', '16.0687427,108.2217626', 'nhabepchohan36.jpg', 4, 'Nhà Bếp Chợ Hàn là một trong những địa điểm ẩm thực nổi bật tại Đà Nẵng, mang đậm hương vị truyền thống. Nếu bạn có dịp đến Đà Nẵng, Nhà Bếp Chợ Hàn chắc chắn sẽ là một địa điểm lý tưởng để thưởng thức ẩm thực địa phương!', 1, '2024-10-12 09:02:55', '2024-10-12 10:17:01'),
(4, 'Nhà hàng Thìa Gỗ', 4, '53 Phan Thúc Duyện, Bắc Mỹ An, Ngũ Hành Sơn, Đà Nẵng, Việt Nam', '16.0529867,108.2390028', 'caption30.jpg', 7, 'Nhà hàng Việt Nam Thìa Gỗ Đà Nẵng\r\nNằm trên một trong những con đường yên tĩnh nhất của trung tâm thành phố và cách các điểm tham quan không xa, Thìa Gỗ đã nhận được nhiều lời khen ngợi về một trong những nhà hàng tốt nhất tại Đà Nẵng.', 1, '2024-10-15 10:30:54', '2024-10-15 10:30:54'),
(5, 'Cabanon Place', 5, 'Cordial Grand Hotel, 27-29 Loseby, Street, Sơn Trà, Đà Nẵng, Việt Nam', '16.0737348,108.2382648', 'Screenshot_16-10-2024_04716_cabanonpalace66.jpeg', 8, 'Cabanon Place kết hợp các yếu tố hiện đại với nét quyến rũ của tầng lớp tư sản Pháp những năm 1960, đưa du khách đến một kỷ nguyên khác thông qua bầu không khí tinh tế và thanh lịch của nó.', 1, '2024-10-15 10:49:35', '2024-10-15 10:49:35'),
(6, 'Thai Market', 4, '183 Nguyễn Văn Thoại, Phường Hải Đông, Quận Sơn Trà, Thành Phố Đà Nẵng', '16.0639179,108.226086', 'Screenshot_16-10-2024_205515_docs40.jpeg', 8, 'Thái Lan mà những kẻ lữ hành say mê nhắc đến là mái nhà gỗ với mấy hoa văn nối tiếp nhau, những con phố chật kín tiếng rao của mấy cô hàng quán, những lũ lượt của dòng xe Tuk Tuk', 1, '2024-10-16 06:55:51', '2024-10-16 06:55:51'),
(7, 'Phố nướng Tokyo', 5, 'Số 4 đường Phạm Văn Đồng, Phường An Hải Bắc, Quận Sơn Trà, Thành Phố Đà Nẵng', '16.070593,108.2380433', 'Screenshot_16-10-2024_211315_docs84.jpeg', 7, '𝐔Ố𝐍𝐆 𝐁𝐈𝐀 𝐊𝐇Ô𝐍𝐆 ĐỂ 𝐆𝐈Ả𝐈 𝐒Ầ𝐔 𝐔Ố𝐍𝐆 𝐁𝐈𝐀 ĐỂ 𝐁𝐈Ế𝐓 𝐓𝐑𝐎𝐍𝐆 ĐẦ𝐔 𝐍𝐇Ớ 𝐀𝐈 Đà Nẵng gió nhẹ, mưa lay kiểu này mà làm ngay tháp bia tươi', 1, '2024-10-16 07:15:31', '2024-10-16 07:15:47'),
(8, 'Madam Lân', 4, 'Số 04 Bạch Đằng, Phường Thạch Thang, Q. Hải Châu, TP. Đà Nẵng', '16.0814063,108.2206779', 'Screenshot_16-10-2024_213833_docs73.jpeg', 7, 'Ra đời vào năm 2012, Nhà hàng Madame Lân là chốn dừng chân của trải nghiệm ẩm thực trọn vẹn bên bờ sông Hàn - trái tim giữa lòng thành phố xinh đẹp Đà Nẵng.', 1, '2024-10-16 07:39:03', '2024-10-16 07:39:03'),
(9, 'Làng Nghệ', 4, '119 Lê Lợi, Hải Châu  Đà Nẵng', '16.0752436,108.217423', 'Screenshot_16-10-2024_215531_docs70.jpeg', 9, 'Đến với nhà hàng Làng Nghệ, không những được đắm chìm tronng khung cảnh mộc mạc làng quê quý thực khách còn được phục vụ những món ăn dân giã, đặc biệt là các món ăn dân giã miền quê Nghệ An', 1, '2024-10-16 07:57:07', '2024-10-16 07:57:07');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_roles`
--

CREATE TABLE `tbl_roles` (
  `roles_id` int(11) NOT NULL,
  `roles_name` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_roles`
--

INSERT INTO `tbl_roles` (`roles_id`, `roles_name`) VALUES
(1, 'admin'),
(2, 'manager'),
(3, 'employee'),
(4, 'hotel_manager');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_room`
--

CREATE TABLE `tbl_room` (
  `room_id` int(10) UNSIGNED NOT NULL,
  `hotel_id` int(11) NOT NULL,
  `room_name` varchar(256) NOT NULL,
  `room_amount_of_people` int(2) NOT NULL,
  `room_acreage` int(11) NOT NULL,
  `room_view` varchar(256) NOT NULL,
  `room_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_room`
--

INSERT INTO `tbl_room` (`room_id`, `hotel_id`, `room_name`, `room_amount_of_people`, `room_acreage`, `room_view`, `room_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(2, 3, 'Phòng Grand Suite', 2, 45, 'Hướng Sông', 1, '2022-11-06 16:58:38', '2022-11-11 16:19:02', NULL),
(3, 3, 'Phòng Deluxe King', 2, 45, 'Hướng Thành Phố Và Sông', 1, '2022-11-06 17:37:43', '2022-11-11 16:19:05', NULL),
(4, 3, 'Phòng Deluxe King', 2, 45, 'Hướng Thành Phố Và Sông', 1, '2022-11-06 17:38:54', '2022-11-06 17:39:00', '2022-11-06 10:39:00'),
(5, 3, 'Phòng Premier Deluxe Twin', 2, 45, 'Hướng Sông', 1, '2022-11-06 17:39:28', NULL, NULL),
(6, 2, 'Deluxe Room', 2, 41, 'Hướng Thành Phố', 1, '2022-11-12 13:36:50', NULL, NULL),
(7, 2, 'Deluxe Room Horizon View', 2, 42, 'Hướng Thành Phố', 1, '2022-11-12 13:37:26', NULL, NULL),
(8, 2, 'Grand Premium Room', 2, 42, 'Hướng Sông', 1, '2022-11-12 13:37:45', NULL, NULL),
(9, 4, 'Phòng Deluxe King', 1, 45, 'Hướng Sông', 1, '2022-11-12 13:44:38', NULL, NULL),
(10, 4, 'Phòng Premier Deluxe Twin', 2, 42, 'Hướng Sông', 1, '2022-11-12 13:44:48', NULL, NULL),
(11, 4, 'Deluxe Room', 3, 45, 'Hướng Thành Phố', 1, '2022-11-12 13:44:57', NULL, NULL),
(12, 5, 'Phòng Deluxe King', 1, 45, 'Hướng Sông', 1, '2022-11-12 13:48:49', NULL, NULL),
(13, 5, 'Phòng Premier Deluxe Twin', 2, 42, 'Hướng Sông', 1, '2022-11-12 13:48:57', NULL, NULL),
(14, 5, 'Phòng Deluxe Twin', 3, 45, 'Hướng Thành Phố', 1, '2022-11-12 13:49:07', NULL, NULL),
(15, 6, 'Superior City View Twin', 2, 32, 'Hướng Thành Phố', 1, '2022-12-23 08:29:54', NULL, NULL),
(16, 6, 'Superior City View Queen Bed', 2, 45, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 08:31:27', NULL, NULL),
(17, 6, 'Superior Ocean View Twin', 2, 42, 'Hướng Thành Phố', 1, '2022-12-23 08:31:50', NULL, NULL),
(18, 7, 'Deluxe Twin Room', 2, 28, 'Hướng Sông', 1, '2022-12-23 08:44:29', NULL, NULL),
(19, 7, 'Deluxe Double City View', 2, 28, 'Hướng Thành Phố', 1, '2022-12-23 08:44:57', NULL, NULL),
(20, 7, 'Premium Ocean View', 2, 30, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 08:45:19', NULL, NULL),
(21, 8, 'Superior Twin', 2, 30, 'Hướng Sông', 1, '2022-12-23 09:04:27', NULL, NULL),
(22, 8, 'Deluxe Twin', 2, 28, 'Hướng Sông', 1, '2022-12-23 09:04:42', NULL, NULL),
(23, 8, 'Suite Double', 2, 30, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 09:04:56', NULL, NULL),
(24, 9, 'Deluxe Double Panoramic Ocean View', 2, 70, 'Hướng Sông', 1, '2022-12-23 09:25:34', NULL, NULL),
(25, 9, 'Deluxe Twin Panoramic Ocean View', 2, 70, 'Hướng Sông', 1, '2022-12-23 09:25:52', NULL, NULL),
(26, 9, 'Premium Deluxe Double Panoramic Ocean View', 2, 70, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 09:26:03', NULL, NULL),
(27, 10, 'Deluxe Ocean Twin, Ban Công, Hướng Biển', 2, 42, 'Hướng Sông', 1, '2022-12-23 18:24:45', NULL, NULL),
(28, 10, 'Deluxe Ocean Double, Ban Công, Hướng Biển', 2, 42, 'Hướng Thành Phố', 1, '2022-12-23 18:25:01', NULL, NULL),
(29, 10, 'Premier Oceanfront Twin, Trực Diện Biển, Tầng cao, Ban Công', 2, 45, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 18:25:21', '2024-11-12 16:56:59', NULL),
(30, 11, 'Superior Twin', 2, 26, 'Hướng Sông', 1, '2022-12-23 18:35:26', NULL, NULL),
(31, 11, 'Superior King', 2, 42, 'Hướng Sông', 1, '2022-12-23 18:35:41', NULL, NULL),
(32, 11, 'Deluxe King', 2, 28, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 18:35:55', NULL, NULL),
(33, 12, 'Superior I Double/Twin', 2, 30, 'Hướng Sông', 1, '2022-12-23 18:44:23', NULL, NULL),
(34, 12, 'Superior II Double/Twin', 2, 32, 'Hướng Sông', 1, '2022-12-23 18:44:44', NULL, NULL),
(35, 12, 'SENIOR DOUBLE', 2, 30, 'Hướng Thành Phố', 1, '2022-12-23 18:45:33', NULL, NULL),
(36, 13, 'Superior Double Or Twin Room', 2, 45, 'Hướng Sông', 1, '2022-12-23 18:55:07', NULL, NULL),
(37, 13, 'Deluxe Double Or Twin Balcony Room', 2, 42, 'Hướng Thành Phố', 1, '2022-12-23 18:55:21', NULL, NULL),
(38, 13, 'Deluxe Triple Balcony Room', 2, 42, 'Hướng Thành Phố Và Sông', 1, '2022-12-23 18:55:34', NULL, NULL),
(39, 14, 'Superior Double city View', 2, 30, 'Hướng Sông', 1, '2022-12-23 19:05:00', NULL, NULL),
(40, 14, 'Superior Twin', 2, 28, 'Hướng Thành Phố', 1, '2022-12-23 19:05:15', NULL, NULL),
(41, 14, 'Deluxe Double', 2, 42, 'Hướng Thành Phố', 1, '2022-12-23 19:05:29', NULL, NULL),
(42, 15, 'Superior King Ocean View', 2, 42, 'Hướng Sông', 1, '2022-12-24 02:33:50', NULL, NULL),
(43, 15, 'Superior Twin Bay View', 2, 28, 'Hướng Sông', 1, '2022-12-24 02:34:03', NULL, NULL),
(44, 15, 'Deluxe King/Twin Ocean View', 2, 42, 'Hướng Thành Phố Và Sông', 1, '2022-12-24 02:34:15', NULL, NULL),
(45, 16, 'Deluxe Twin', 2, 28, 'Hướng Sông', 1, '2022-12-24 02:43:31', NULL, NULL),
(46, 16, 'Deluxe Partial Ocean Twin', 2, 30, 'Hướng Thành Phố Và Sông', 1, '2022-12-24 02:43:44', NULL, NULL),
(47, 16, 'Deluxe Partial Ocean King', 2, 30, 'Hướng Thành Phố', 1, '2022-12-24 02:43:56', NULL, NULL),
(48, 17, 'Superior Twin/King (Khách Việt Nam)', 2, 37, 'Hướng Thành Phố', 1, '2022-12-24 02:52:19', NULL, NULL),
(49, 17, 'Deluxe Twin/King (Khách Việt Nam)', 2, 30, 'Hướng Thành Phố', 1, '2022-12-24 02:52:33', NULL, NULL),
(50, 17, 'Deluxe Golden Bay King/Twin (Khách Việt Nam)', 2, 28, 'Hướng Thành Phố Và Sông', 1, '2022-12-24 02:52:47', NULL, NULL),
(51, 18, 'Deluxe City View', 2, 28, 'Hướng Thành Phố', 1, '2022-12-24 03:00:53', NULL, NULL),
(52, 18, 'Deluxe Partial Ocean View', 2, 30, 'Hướng Thành Phố Và Sông', 1, '2022-12-24 03:01:07', NULL, NULL),
(53, 18, 'Junior Suite Ocean View', 2, 28, 'Hướng Thành Phố', 1, '2022-12-24 03:01:19', NULL, NULL),
(54, 19, 'Superior King Room', 2, 45, 'Hướng Sông', 1, '2022-12-24 03:10:02', NULL, NULL),
(55, 19, 'Deluxe King Room', 2, 45, 'Hướng Sông', 1, '2022-12-24 03:10:16', NULL, NULL),
(56, 19, 'Deluxe King Room with Street View', 2, 45, 'Hướng Thành Phố', 1, '2022-12-24 03:10:35', NULL, NULL),
(57, 20, 'Classic Double', 2, 45, 'Hướng Sông', 1, '2022-12-24 03:19:38', NULL, NULL),
(58, 20, 'Deluxe Twin city view', 2, 42, 'Hướng Thành Phố Và Sông', 1, '2022-12-24 03:19:52', NULL, NULL),
(59, 20, 'Premium Sea Side Twin', 2, 28, 'Hướng Thành Phố', 1, '2022-12-24 03:20:05', NULL, NULL),
(60, 21, 'Superior King Room', 2, 28, 'Hướng Sông', 1, '2022-12-24 03:27:34', NULL, NULL),
(61, 21, 'Deluxe King Có Ban Công View Hồ Bơi/Thành Phố', 2, 45, 'Hướng Thành Phố', 1, '2022-12-24 03:27:53', NULL, NULL),
(62, 21, 'Superior Twin Room', 2, 42, 'Hướng Thành Phố', 1, '2022-12-24 03:28:06', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_servicecharge`
--

CREATE TABLE `tbl_servicecharge` (
  `servicecharge_id` int(10) NOT NULL,
  `hotel_id` int(10) NOT NULL,
  `servicecharge_condition` int(1) NOT NULL,
  `servicecharge_fee` int(200) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_servicecharge`
--

INSERT INTO `tbl_servicecharge` (`servicecharge_id`, `hotel_id`, `servicecharge_condition`, `servicecharge_fee`, `created_at`, `updated_at`, `deleted_at`) VALUES
(5, 2, 1, 10, '2022-11-17 13:40:02', '2022-11-23 15:52:55', NULL),
(6, 4, 1, 11, '2022-11-17 13:40:10', NULL, NULL),
(7, 5, 1, 12, '2022-11-17 13:49:49', NULL, NULL),
(8, 3, 2, 100000, '2022-11-20 10:05:56', '2022-11-23 15:52:53', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_slider`
--

CREATE TABLE `tbl_slider` (
  `slider_id` int(10) UNSIGNED NOT NULL,
  `slider_name` varchar(255) NOT NULL,
  `slider_image` text NOT NULL,
  `slider_link` varchar(256) NOT NULL DEFAULT '#',
  `slider_status` varchar(255) NOT NULL,
  `slider_desc` text NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_slider`
--

INSERT INTO `tbl_slider` (`slider_id`, `slider_name`, `slider_image`, `slider_link`, `slider_status`, `slider_desc`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 'Slider Sale', 'slider56.jfif', '#', '1', '<p>Slider Sale</p>', '2022-10-23 09:49:39', '2022-12-26 10:11:31', NULL),
(2, 'Slider Giới Thiệu Bạn Bè', 'slider111.jfif', '#', '1', '<p>Slider Giới Thiệu Bạn Bè</p>', '2022-10-23 09:50:13', '2022-12-26 10:11:29', NULL),
(3, 'Slider Sale', 'slider284.jfif', '#', '1', '<p>Slider Sale</p>', '2022-10-23 09:50:30', '2022-12-26 10:11:27', NULL),
(4, 'Slider Super Sale', 'slider364.jfif', '#', '1', '<p>Slider Super Sale</p>', '2022-10-23 09:50:54', '2022-10-29 13:33:21', NULL),
(5, 'Slider', 'slider413.jfif', '#', '1', 'Hư Cấu', '2022-10-23 09:51:16', '2022-10-30 17:18:24', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_social`
--

CREATE TABLE `tbl_social` (
  `user_id` int(11) NOT NULL,
  `provider_user_id` varchar(100) NOT NULL,
  `provider` varchar(100) NOT NULL,
  `user` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_social`
--

INSERT INTO `tbl_social` (`user_id`, `provider_user_id`, `provider`, `user`, `created_at`, `deleted_at`) VALUES
(9, '100045168716516445279', 'google', 13, '2022-12-23 07:53:13', NULL),
(10, '107011816793554220452', 'google', 3, '2023-08-18 04:11:21', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_statistical`
--

CREATE TABLE `tbl_statistical` (
  `statistical_id` int(11) NOT NULL,
  `order_date` varchar(100) NOT NULL,
  `sales` varchar(200) NOT NULL,
  `order_refused` int(200) NOT NULL,
  `price_order_refused` int(255) NOT NULL,
  `quantity_order_room` int(11) NOT NULL,
  `total_order` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `tbl_statistical`
--

INSERT INTO `tbl_statistical` (`statistical_id`, `order_date`, `sales`, `order_refused`, `price_order_refused`, `quantity_order_room`, `total_order`) VALUES
(1, '2022-12-15', '6016000', 0, 0, 2, 2),
(2, '2022-12-16', '648000', 0, 0, 6, 2),
(3, '2022-12-17', '4270000', 0, 0, 17, 4),
(4, '2022-12-18', '12169460', 0, 0, 2, 3),
(5, '2022-12-24', '18837137.4724', 1, 11838960, 7, 9),
(10, '2022-12-25', '8762360', 0, 0, 2, 3),
(11, '2023-08-18', '1377000', 0, 0, 1, 2),
(12, '2023-11-14', '0', 0, 0, 0, 0),
(13, '2024-05-04', '0', 0, 0, 0, 0),
(14, '2024-05-05', '0', 0, 0, 0, 0),
(15, '2024-05-06', '0', 0, 0, 0, 0),
(16, '2024-06-04', '6916000', 2, 8050460, 1, 4),
(17, '2024-11-06', '0', 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_table_restaurant`
--

CREATE TABLE `tbl_table_restaurant` (
  `table_id` int(11) NOT NULL,
  `restaurant_id` int(11) NOT NULL,
  `table_price` double NOT NULL,
  `table_name` varchar(255) NOT NULL,
  `table_condition` int(10) DEFAULT NULL,
  `table_quantity` int(10) NOT NULL,
  `table_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_table_restaurant`
--

INSERT INTO `tbl_table_restaurant` (`table_id`, `restaurant_id`, `table_price`, `table_name`, `table_condition`, `table_quantity`, `table_status`, `created_at`, `updated_at`) VALUES
(1, 1, 100000, 'Bàn 1', NULL, 10, 1, '2024-10-12 18:43:45', '2024-10-12 18:43:45'),
(5, 1, 50000, 'Bàn cao cấp', NULL, 10, 1, '2024-10-15 16:52:52', '2024-10-15 16:52:52');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_type_room`
--

CREATE TABLE `tbl_type_room` (
  `type_room_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `type_room_bed` int(11) NOT NULL,
  `type_room_price` double NOT NULL,
  `type_room_condition` int(11) NOT NULL,
  `type_room_price_sale` double DEFAULT NULL,
  `type_room_quantity` int(10) NOT NULL,
  `type_room_status` int(1) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_type_room`
--

INSERT INTO `tbl_type_room` (`type_room_id`, `room_id`, `type_room_bed`, `type_room_price`, `type_room_condition`, `type_room_price_sale`, `type_room_quantity`, `type_room_status`, `created_at`, `updated_at`, `deleted_at`) VALUES
(1, 2, 2, 1400000, 1, 9, 19, 1, '2022-11-10 17:17:24', '2024-05-05 12:50:42', NULL),
(2, 3, 1, 1500000, 1, 8, 0, 1, '2022-11-10 17:19:55', '2022-11-12 17:50:33', NULL),
(3, 5, 3, 1500000, 0, NULL, 15, 1, '2022-11-10 17:20:15', '2024-06-04 12:54:36', NULL),
(4, 2, 2, 1500000, 0, NULL, 20, 1, '2022-11-12 08:47:51', '2022-12-25 00:50:09', NULL),
(6, 2, 1, 999999, 1, 8, 20, 1, '2022-11-12 08:51:58', '2022-12-25 00:50:16', NULL),
(7, 6, 1, 1305636, 1, 10, 18, 1, '2022-11-12 13:38:28', '2024-05-05 13:13:33', NULL),
(8, 6, 2, 1500000, 0, NULL, 20, 1, '2022-11-12 13:39:15', '2022-12-24 13:00:30', NULL),
(9, 7, 1, 1400000, 1, 7, 0, 1, '2022-11-12 13:39:30', '2022-11-12 13:42:02', NULL),
(10, 6, 3, 1600000, 1, 8, 0, 1, '2022-11-12 13:40:11', '2022-11-12 13:40:33', NULL),
(11, 7, 2, 1305636, 0, NULL, 0, 1, '2022-11-12 13:41:28', NULL, NULL),
(12, 7, 2, 999999, 1, 8, 0, 1, '2022-11-12 13:41:45', '2022-11-12 13:41:54', NULL),
(13, 8, 1, 1200000, 0, NULL, 0, 1, '2022-11-12 13:42:15', NULL, NULL),
(14, 8, 1, 1200000, 0, NULL, 0, 1, '2022-11-12 13:42:15', NULL, NULL),
(15, 8, 2, 1500000, 1, 12, 0, 1, '2022-11-12 13:42:30', NULL, NULL),
(16, 6, 1, 1100000, 0, NULL, 20, 1, '2022-11-12 13:43:42', '2022-12-24 13:00:38', NULL),
(17, 9, 1, 1530000, 0, NULL, 0, 1, '2022-11-12 13:45:14', '2022-12-22 17:04:33', NULL),
(18, 9, 2, 999999, 1, 19, 0, 1, '2022-11-12 13:45:42', NULL, NULL),
(19, 9, 3, 1500000, 1, 15, 0, 1, '2022-11-12 13:45:58', NULL, NULL),
(20, 10, 1, 1400000, 0, NULL, 0, 1, '2022-11-12 13:46:24', NULL, NULL),
(21, 10, 2, 1200000, 1, 16, 0, 1, '2022-11-12 13:46:40', NULL, NULL),
(22, 10, 3, 1500000, 1, 13, 0, 1, '2022-11-12 13:46:56', NULL, NULL),
(23, 11, 1, 1500000, 0, NULL, 0, 1, '2022-11-12 13:47:12', NULL, NULL),
(24, 11, 2, 1500000, 1, 17, 0, 1, '2022-11-12 13:47:23', NULL, NULL),
(25, 11, 3, 1305636, 1, 17, 0, 1, '2022-11-12 13:47:41', NULL, NULL),
(26, 12, 1, 800000, 1, 13, 0, 1, '2022-11-12 13:49:15', '2022-11-12 14:18:38', NULL),
(27, 12, 2, 1500000, 1, 42, 0, 1, '2022-11-12 13:49:34', NULL, NULL),
(28, 12, 3, 1500000, 1, 23, 0, 1, '2022-11-12 13:49:48', NULL, NULL),
(29, 13, 1, 1234440, 0, NULL, 0, 1, '2022-11-12 13:50:06', NULL, NULL),
(30, 13, 2, 1500000, 1, 24, 0, 1, '2022-11-12 13:50:34', NULL, NULL),
(31, 13, 3, 1200000, 1, 26, 0, 1, '2022-11-12 13:50:51', NULL, NULL),
(32, 14, 1, 1235555, 0, NULL, 0, 1, '2022-11-12 13:51:17', NULL, NULL),
(33, 14, 2, 1200000, 1, 27, 0, 1, '2022-11-12 13:51:33', NULL, NULL),
(34, 14, 3, 1454533, 1, 21, 0, 1, '2022-11-12 13:52:00', NULL, NULL),
(35, 12, 1, 1200000, 0, NULL, 0, 1, '2022-11-12 15:11:28', '2022-11-12 15:11:36', '2022-11-12 08:11:36'),
(36, 12, 1, 1200000, 0, NULL, 0, 1, '2022-11-12 15:12:40', '2022-11-12 15:12:44', '2022-11-12 08:12:44'),
(37, 3, 3, 1600000, 1, 33, 0, 1, '2022-11-13 00:48:29', NULL, NULL),
(38, 3, 3, 1700000, 1, 9, 0, 1, '2022-11-13 00:49:03', NULL, NULL),
(39, 5, 3, 1700000, 0, NULL, 0, 1, '2022-11-13 00:49:15', NULL, NULL),
(40, 5, 3, 1700000, 1, 17, 19, 1, '2022-11-13 00:49:34', '2024-05-05 12:38:04', NULL),
(42, 2, 3, 1305636, 1, 10, 20, 1, '2022-12-22 17:30:14', '2022-12-22 17:40:38', NULL),
(43, 15, 3, 1200000, 1, 13, 19, 1, '2022-12-23 08:32:42', '2022-12-24 15:39:37', NULL),
(44, 15, 1, 1350000, 0, NULL, 20, 1, '2022-12-23 08:50:25', NULL, NULL),
(45, 15, 3, 1700000, 1, 17, 20, 1, '2022-12-23 08:50:42', NULL, NULL),
(46, 16, 2, 1450000, 0, NULL, 30, 1, '2022-12-23 08:51:03', NULL, NULL),
(47, 16, 2, 1700000, 1, 13, 30, 1, '2022-12-23 08:51:22', NULL, NULL),
(48, 16, 3, 1750000, 0, NULL, 20, 1, '2022-12-23 08:51:37', NULL, NULL),
(49, 17, 1, 1100000, 0, NULL, 20, 1, '2022-12-23 08:51:52', NULL, NULL),
(50, 17, 2, 1756000, 1, 12, 20, 1, '2022-12-23 08:52:24', NULL, NULL),
(51, 17, 3, 1705636, 0, NULL, 20, 1, '2022-12-23 08:52:39', NULL, NULL),
(52, 21, 2, 1240000, 0, NULL, 20, 1, '2022-12-23 09:07:25', NULL, NULL),
(53, 21, 2, 1700000, 1, 18, 20, 1, '2022-12-23 09:07:39', NULL, NULL),
(54, 21, 3, 1770000, 0, NULL, 20, 1, '2022-12-23 09:07:54', NULL, NULL),
(55, 22, 1, 1280000, 0, NULL, 20, 1, '2022-12-23 09:08:10', NULL, NULL),
(56, 22, 2, 1570000, 1, 9, 20, 1, '2022-12-23 09:08:23', NULL, NULL),
(57, 22, 3, 1790000, 1, 12, 20, 1, '2022-12-23 09:08:39', NULL, NULL),
(58, 23, 1, 1520000, 0, NULL, 20, 1, '2022-12-23 09:08:51', NULL, NULL),
(59, 23, 2, 1560000, 1, 10, 20, 1, '2022-12-23 09:09:05', NULL, NULL),
(60, 23, 3, 1730000, 1, 9, 20, 1, '2022-12-23 09:09:35', NULL, NULL),
(61, 24, 1, 2300000, 0, NULL, 20, 1, '2022-12-23 09:28:19', NULL, NULL),
(62, 24, 2, 3450000, 1, 21, 20, 1, '2022-12-23 09:28:45', '2022-12-23 12:45:47', NULL),
(63, 24, 3, 5350000, 1, 19, 20, 1, '2022-12-23 09:29:05', '2022-12-23 12:45:42', NULL),
(64, 25, 1, 2500000, 0, NULL, 20, 1, '2022-12-23 09:29:20', NULL, NULL),
(65, 25, 2, 4500000, 1, 25, 30, 1, '2022-12-23 09:29:37', NULL, NULL),
(66, 25, 3, 5060300, 1, 19, 20, 1, '2022-12-23 09:29:58', NULL, NULL),
(67, 26, 1, 2700000, 1, 22, 20, 1, '2022-12-23 09:30:15', NULL, NULL),
(68, 26, 2, 3400040, 1, 34, 20, 1, '2022-12-23 09:30:35', NULL, NULL),
(69, 26, 3, 5400000, 1, 20, 30, 1, '2022-12-23 09:30:54', NULL, NULL),
(70, 20, 3, 4200000, 1, 13, 20, 1, '2022-12-23 11:57:21', '2022-12-23 17:06:32', NULL),
(71, 20, 3, 4800000, 1, 9, 30, 1, '2022-12-23 11:57:47', NULL, NULL),
(72, 19, 3, 3500000, 0, NULL, 20, 1, '2022-12-23 11:58:05', NULL, NULL),
(73, 18, 2, 1700000, 1, 9, 20, 1, '2022-12-23 11:58:20', NULL, NULL),
(74, 18, 3, 3400000, 1, 17, 30, 1, '2022-12-23 11:58:40', NULL, NULL),
(75, 27, 1, 3400000, 1, 34, 20, 1, '2022-12-23 18:28:14', NULL, NULL),
(76, 27, 2, 4305636, 1, 22, 20, 1, '2022-12-23 18:28:35', NULL, NULL),
(77, 28, 1, 5700000, 1, 26, 20, 1, '2022-12-23 18:29:12', NULL, NULL),
(78, 28, 3, 4500000, 1, 10, 20, 1, '2022-12-23 18:29:35', NULL, NULL),
(79, 29, 2, 4280000, 1, 17, 20, 1, '2022-12-23 18:29:57', NULL, NULL),
(80, 29, 2, 4200000, 1, 13, 20, 1, '2022-12-23 18:30:14', NULL, NULL),
(81, 30, 2, 3400000, 1, 34, 20, 1, '2022-12-23 18:38:27', NULL, NULL),
(82, 30, 2, 4500400, 1, 19, 30, 1, '2022-12-23 18:38:53', NULL, NULL),
(83, 31, 1, 2450000, 1, 23, 20, 1, '2022-12-23 18:39:12', NULL, NULL),
(84, 31, 2, 4507800, 1, 23, 20, 1, '2022-12-23 18:39:34', NULL, NULL),
(85, 32, 1, 2500000, 0, NULL, 19, 1, '2022-12-23 18:39:50', '2022-12-24 12:00:55', NULL),
(86, 32, 2, 4500000, 1, 12, 20, 1, '2022-12-23 18:40:03', NULL, NULL),
(87, 33, 1, 2700000, 1, 32, 20, 1, '2022-12-23 18:49:22', NULL, NULL),
(88, 33, 2, 4350000, 1, 32, 30, 1, '2022-12-23 18:49:38', NULL, NULL),
(89, 34, 1, 1500000, 0, NULL, 20, 1, '2022-12-23 18:49:51', NULL, NULL),
(90, 34, 2, 3500000, 1, 24, 20, 1, '2022-12-23 18:50:07', NULL, NULL),
(91, 35, 1, 1600000, 0, NULL, 20, 1, '2022-12-23 18:50:22', NULL, NULL),
(92, 34, 2, 4500000, 1, 22, 20, 1, '2022-12-23 18:50:39', NULL, NULL),
(93, 35, 2, 2200000, 0, NULL, 19, 1, '2022-12-23 18:50:53', '2022-12-24 09:27:32', NULL),
(94, 36, 1, 2500000, 0, NULL, 20, 1, '2022-12-23 18:58:06', NULL, NULL),
(95, 36, 2, 4700000, 1, 10, 20, 1, '2022-12-23 18:58:21', NULL, NULL),
(96, 37, 1, 1500000, 1, 7, 20, 1, '2022-12-23 18:58:34', NULL, NULL),
(97, 37, 2, 4500000, 1, 13, 20, 1, '2022-12-23 18:58:49', NULL, NULL),
(98, 38, 1, 1500000, 1, 10, 20, 1, '2022-12-23 18:59:03', NULL, NULL),
(99, 38, 2, 2506000, 1, 8, 20, 1, '2022-12-23 18:59:21', NULL, NULL),
(100, 39, 1, 1400000, 1, 7, 30, 1, '2022-12-23 19:07:57', NULL, NULL),
(101, 39, 2, 4500000, 1, 17, 20, 1, '2022-12-23 19:08:14', NULL, NULL),
(102, 40, 1, 1400000, 1, 23, 30, 1, '2022-12-23 19:08:28', NULL, NULL),
(103, 40, 2, 1305636, 1, 7, 20, 1, '2022-12-23 19:08:40', NULL, NULL),
(104, 40, 3, 4305636, 1, 13, 20, 1, '2022-12-23 19:08:54', NULL, NULL),
(105, 41, 1, 1400000, 0, NULL, 20, 1, '2022-12-23 19:09:04', NULL, NULL),
(106, 41, 2, 2500000, 1, 9, 20, 1, '2022-12-23 19:09:19', NULL, NULL),
(107, 41, 1, 2500000, 1, 10, 20, 1, '2022-12-23 19:09:33', NULL, NULL),
(108, 41, 1, 1305636, 0, NULL, 20, 1, '2022-12-23 19:09:48', NULL, NULL),
(109, 42, 1, 1700000, 1, 13, 20, 1, '2022-12-24 02:36:44', NULL, NULL),
(110, 42, 2, 3706000, 1, 9, 20, 1, '2022-12-24 02:37:03', NULL, NULL),
(111, 42, 1, 4500000, 0, NULL, 30, 1, '2022-12-24 02:37:14', NULL, NULL),
(112, 43, 1, 1704000, 0, NULL, 20, 1, '2022-12-24 02:37:33', NULL, NULL),
(113, 43, 2, 4556000, 1, 8, 20, 1, '2022-12-24 02:37:49', NULL, NULL),
(114, 44, 1, 1400000, 0, NULL, 20, 1, '2022-12-24 02:38:00', NULL, NULL),
(115, 44, 2, 4500000, 1, 17, 20, 1, '2022-12-24 02:38:14', NULL, NULL),
(116, 44, 3, 1305636, 0, NULL, 20, 1, '2022-12-24 02:38:27', NULL, NULL),
(117, 45, 1, 1703000, 1, 7, 20, 1, '2022-12-24 02:46:22', NULL, NULL),
(118, 45, 2, 4500301, 1, 10, 20, 1, '2022-12-24 02:46:44', NULL, NULL),
(119, 45, 3, 4502000, 0, NULL, 20, 1, '2022-12-24 02:47:02', NULL, NULL),
(120, 46, 1, 1701000, 0, NULL, 30, 1, '2022-12-24 02:47:14', NULL, NULL),
(121, 46, 2, 2700000, 1, 22, 20, 1, '2022-12-24 02:47:31', NULL, NULL),
(122, 47, 1, 1400000, 0, NULL, 20, 1, '2022-12-24 02:47:43', NULL, NULL),
(123, 47, 3, 4500000, 1, 11, 20, 1, '2022-12-24 02:47:56', NULL, NULL),
(124, 46, 2, 3700000, 1, 17, 30, 1, '2022-12-24 02:48:14', NULL, NULL),
(125, 48, 1, 2300000, 1, 11, 20, 1, '2022-12-24 02:54:55', NULL, NULL),
(126, 48, 2, 4500000, 1, 12, 30, 1, '2022-12-24 02:55:07', NULL, NULL),
(127, 48, 3, 4500000, 1, 32, 20, 1, '2022-12-24 02:55:21', NULL, NULL),
(128, 49, 1, 2200000, 1, 22, 29, 1, '2022-12-24 02:55:35', '2023-11-12 16:52:04', NULL),
(129, 49, 2, 3700000, 1, 13, 20, 1, '2022-12-24 02:55:49', NULL, NULL),
(130, 50, 1, 1700000, 0, NULL, 18, 1, '2022-12-24 02:56:00', '2023-08-18 14:04:44', NULL),
(131, 50, 2, 2500000, 1, 15, 20, 1, '2022-12-24 02:56:17', NULL, NULL),
(132, 51, 1, 1200000, 1, 9, 20, 1, '2022-12-24 03:03:00', NULL, NULL),
(133, 51, 2, 2700000, 1, 7, 29, 1, '2022-12-24 03:03:16', '2022-12-24 10:28:35', NULL),
(134, 51, 3, 4500000, 1, 24, 30, 1, '2022-12-24 03:03:34', NULL, NULL),
(135, 52, 1, 1400000, 0, NULL, 20, 1, '2022-12-24 03:03:46', NULL, NULL),
(136, 52, 2, 2300000, 1, 8, 30, 1, '2022-12-24 03:04:01', NULL, NULL),
(137, 52, 3, 4500000, 1, 10, 30, 1, '2022-12-24 03:04:17', NULL, NULL),
(138, 53, 1, 1700000, 1, 9, 20, 1, '2022-12-24 03:04:29', NULL, NULL),
(139, 53, 2, 2700000, 1, 13, 30, 1, '2022-12-24 03:04:45', NULL, NULL),
(140, 54, 1, 2200000, 1, 11, 30, 1, '2022-12-24 03:12:27', NULL, NULL),
(141, 54, 2, 2506000, 1, 19, 20, 1, '2022-12-24 03:12:40', NULL, NULL),
(142, 54, 3, 4350000, 1, 12, 20, 1, '2022-12-24 03:12:53', NULL, NULL),
(143, 55, 1, 1600000, 1, 17, 20, 1, '2022-12-24 03:13:04', NULL, NULL),
(144, 55, 2, 1200000, 1, 11, 20, 1, '2022-12-24 03:13:16', NULL, NULL),
(145, 55, 2, 2506000, 1, 12, 30, 1, '2022-12-24 03:13:32', NULL, NULL),
(146, 56, 1, 1700000, 1, 32, 18, 1, '2022-12-24 03:13:49', '2022-12-25 00:37:12', NULL),
(147, 56, 2, 2500000, 1, 17, 30, 1, '2022-12-24 03:14:06', '2024-06-04 12:46:49', NULL),
(148, 57, 1, 1400000, 1, 23, 20, 1, '2022-12-24 03:22:10', NULL, NULL),
(149, 57, 2, 2506000, 1, 11, 20, 1, '2022-12-24 03:22:23', NULL, NULL),
(150, 57, 3, 4500000, 1, 32, 20, 1, '2022-12-24 03:22:38', NULL, NULL),
(151, 58, 1, 1400000, 1, 7, 20, 1, '2022-12-24 03:22:48', NULL, NULL),
(152, 58, 2, 1200000, 1, 8, 30, 1, '2022-12-24 03:23:00', NULL, NULL),
(153, 58, 3, 2501000, 1, 10, 20, 1, '2022-12-24 03:23:16', NULL, NULL),
(154, 59, 1, 1305636, 0, NULL, 19, 1, '2022-12-24 03:23:29', '2024-05-06 08:33:38', NULL),
(155, 59, 2, 1400000, 0, NULL, 30, 1, '2022-12-24 03:23:44', NULL, NULL),
(156, 60, 1, 2200000, 1, 11, 20, 1, '2022-12-24 03:30:17', NULL, NULL),
(157, 60, 2, 1200000, 0, NULL, 30, 1, '2022-12-24 03:30:27', NULL, NULL),
(158, 60, 3, 2506000, 1, 13, 30, 1, '2022-12-24 03:30:40', NULL, NULL),
(159, 61, 1, 1700000, 1, 9, 19, 1, '2022-12-24 03:30:52', '2022-12-24 13:20:42', NULL),
(160, 61, 2, 1700000, 1, 13, 20, 1, '2022-12-24 03:31:06', NULL, NULL),
(161, 62, 1, 1500000, 1, 13, 19, 1, '2022-12-24 03:31:20', '2022-12-24 13:18:54', NULL),
(162, 62, 2, 1200000, 1, 7, 20, 1, '2022-12-24 03:31:31', NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin_roles`
--
ALTER TABLE `admin_roles`
  ADD PRIMARY KEY (`admin_roles_id`);

--
-- Indexes for table `tbl_activitylog`
--
ALTER TABLE `tbl_activitylog`
  ADD PRIMARY KEY (`activitylog_id`);

--
-- Indexes for table `tbl_admin`
--
ALTER TABLE `tbl_admin`
  ADD PRIMARY KEY (`admin_id`);

--
-- Indexes for table `tbl_area`
--
ALTER TABLE `tbl_area`
  ADD PRIMARY KEY (`area_id`);

--
-- Indexes for table `tbl_bannerads`
--
ALTER TABLE `tbl_bannerads`
  ADD PRIMARY KEY (`bannerads_id`);

--
-- Indexes for table `tbl_brand`
--
ALTER TABLE `tbl_brand`
  ADD PRIMARY KEY (`brand_id`);

--
-- Indexes for table `tbl_company_config`
--
ALTER TABLE `tbl_company_config`
  ADD PRIMARY KEY (`company_id`);

--
-- Indexes for table `tbl_configweb`
--
ALTER TABLE `tbl_configweb`
  ADD PRIMARY KEY (`config_id`);

--
-- Indexes for table `tbl_coupon`
--
ALTER TABLE `tbl_coupon`
  ADD PRIMARY KEY (`coupon_id`);

--
-- Indexes for table `tbl_customers`
--
ALTER TABLE `tbl_customers`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `tbl_evaluate`
--
ALTER TABLE `tbl_evaluate`
  ADD PRIMARY KEY (`evaluate_id`);

--
-- Indexes for table `tbl_evaluate_restaurant`
--
ALTER TABLE `tbl_evaluate_restaurant`
  ADD PRIMARY KEY (`evaluate_id`);

--
-- Indexes for table `tbl_facilitieshotel`
--
ALTER TABLE `tbl_facilitieshotel`
  ADD PRIMARY KEY (`facilitieshotel_id`);

--
-- Indexes for table `tbl_facilitiesroom`
--
ALTER TABLE `tbl_facilitiesroom`
  ADD PRIMARY KEY (`facilitiesroom_id`);

--
-- Indexes for table `tbl_gallery_hotel`
--
ALTER TABLE `tbl_gallery_hotel`
  ADD PRIMARY KEY (`gallery_hotel_id`);

--
-- Indexes for table `tbl_gallery_restaurant`
--
ALTER TABLE `tbl_gallery_restaurant`
  ADD PRIMARY KEY (`gallery_restaurant_id`);

--
-- Indexes for table `tbl_gallery_room`
--
ALTER TABLE `tbl_gallery_room`
  ADD PRIMARY KEY (`gallery_room_id`);

--
-- Indexes for table `tbl_hotel`
--
ALTER TABLE `tbl_hotel`
  ADD PRIMARY KEY (`hotel_id`);

--
-- Indexes for table `tbl_manipulation_activity`
--
ALTER TABLE `tbl_manipulation_activity`
  ADD PRIMARY KEY (`manipulation_activity_id`);

--
-- Indexes for table `tbl_menu_restaurant`
--
ALTER TABLE `tbl_menu_restaurant`
  ADD PRIMARY KEY (`menu_item_id`);

--
-- Indexes for table `tbl_order`
--
ALTER TABLE `tbl_order`
  ADD PRIMARY KEY (`order_id`);

--
-- Indexes for table `tbl_orderer`
--
ALTER TABLE `tbl_orderer`
  ADD PRIMARY KEY (`orderer_id`);

--
-- Indexes for table `tbl_order_details`
--
ALTER TABLE `tbl_order_details`
  ADD PRIMARY KEY (`order_details_id`);

--
-- Indexes for table `tbl_order_details_restaurant`
--
ALTER TABLE `tbl_order_details_restaurant`
  ADD PRIMARY KEY (`order_details_id`);

--
-- Indexes for table `tbl_payment`
--
ALTER TABLE `tbl_payment`
  ADD PRIMARY KEY (`payment_id`);

--
-- Indexes for table `tbl_restaurant`
--
ALTER TABLE `tbl_restaurant`
  ADD PRIMARY KEY (`restaurant_id`);

--
-- Indexes for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  ADD PRIMARY KEY (`roles_id`);

--
-- Indexes for table `tbl_room`
--
ALTER TABLE `tbl_room`
  ADD PRIMARY KEY (`room_id`);

--
-- Indexes for table `tbl_servicecharge`
--
ALTER TABLE `tbl_servicecharge`
  ADD PRIMARY KEY (`servicecharge_id`);

--
-- Indexes for table `tbl_slider`
--
ALTER TABLE `tbl_slider`
  ADD PRIMARY KEY (`slider_id`);

--
-- Indexes for table `tbl_social`
--
ALTER TABLE `tbl_social`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `tbl_statistical`
--
ALTER TABLE `tbl_statistical`
  ADD PRIMARY KEY (`statistical_id`);

--
-- Indexes for table `tbl_table_restaurant`
--
ALTER TABLE `tbl_table_restaurant`
  ADD PRIMARY KEY (`table_id`);

--
-- Indexes for table `tbl_type_room`
--
ALTER TABLE `tbl_type_room`
  ADD PRIMARY KEY (`type_room_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin_roles`
--
ALTER TABLE `admin_roles`
  MODIFY `admin_roles_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `tbl_activitylog`
--
ALTER TABLE `tbl_activitylog`
  MODIFY `activitylog_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=204;

--
-- AUTO_INCREMENT for table `tbl_admin`
--
ALTER TABLE `tbl_admin`
  MODIFY `admin_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `tbl_area`
--
ALTER TABLE `tbl_area`
  MODIFY `area_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `tbl_bannerads`
--
ALTER TABLE `tbl_bannerads`
  MODIFY `bannerads_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tbl_brand`
--
ALTER TABLE `tbl_brand`
  MODIFY `brand_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tbl_company_config`
--
ALTER TABLE `tbl_company_config`
  MODIFY `company_id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `tbl_configweb`
--
ALTER TABLE `tbl_configweb`
  MODIFY `config_id` int(111) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `tbl_coupon`
--
ALTER TABLE `tbl_coupon`
  MODIFY `coupon_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tbl_customers`
--
ALTER TABLE `tbl_customers`
  MODIFY `customer_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `tbl_evaluate`
--
ALTER TABLE `tbl_evaluate`
  MODIFY `evaluate_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=274;

--
-- AUTO_INCREMENT for table `tbl_evaluate_restaurant`
--
ALTER TABLE `tbl_evaluate_restaurant`
  MODIFY `evaluate_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_facilitieshotel`
--
ALTER TABLE `tbl_facilitieshotel`
  MODIFY `facilitieshotel_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `tbl_facilitiesroom`
--
ALTER TABLE `tbl_facilitiesroom`
  MODIFY `facilitiesroom_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tbl_gallery_hotel`
--
ALTER TABLE `tbl_gallery_hotel`
  MODIFY `gallery_hotel_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=349;

--
-- AUTO_INCREMENT for table `tbl_gallery_restaurant`
--
ALTER TABLE `tbl_gallery_restaurant`
  MODIFY `gallery_restaurant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT for table `tbl_gallery_room`
--
ALTER TABLE `tbl_gallery_room`
  MODIFY `gallery_room_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=264;

--
-- AUTO_INCREMENT for table `tbl_hotel`
--
ALTER TABLE `tbl_hotel`
  MODIFY `hotel_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `tbl_manipulation_activity`
--
ALTER TABLE `tbl_manipulation_activity`
  MODIFY `manipulation_activity_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7884;

--
-- AUTO_INCREMENT for table `tbl_menu_restaurant`
--
ALTER TABLE `tbl_menu_restaurant`
  MODIFY `menu_item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `tbl_order`
--
ALTER TABLE `tbl_order`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=124;

--
-- AUTO_INCREMENT for table `tbl_orderer`
--
ALTER TABLE `tbl_orderer`
  MODIFY `orderer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=136;

--
-- AUTO_INCREMENT for table `tbl_order_details`
--
ALTER TABLE `tbl_order_details`
  MODIFY `order_details_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=81;

--
-- AUTO_INCREMENT for table `tbl_order_details_restaurant`
--
ALTER TABLE `tbl_order_details_restaurant`
  MODIFY `order_details_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=155;

--
-- AUTO_INCREMENT for table `tbl_payment`
--
ALTER TABLE `tbl_payment`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=139;

--
-- AUTO_INCREMENT for table `tbl_restaurant`
--
ALTER TABLE `tbl_restaurant`
  MODIFY `restaurant_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  MODIFY `roles_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_room`
--
ALTER TABLE `tbl_room`
  MODIFY `room_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=64;

--
-- AUTO_INCREMENT for table `tbl_servicecharge`
--
ALTER TABLE `tbl_servicecharge`
  MODIFY `servicecharge_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tbl_slider`
--
ALTER TABLE `tbl_slider`
  MODIFY `slider_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `tbl_social`
--
ALTER TABLE `tbl_social`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tbl_statistical`
--
ALTER TABLE `tbl_statistical`
  MODIFY `statistical_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `tbl_table_restaurant`
--
ALTER TABLE `tbl_table_restaurant`
  MODIFY `table_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `tbl_type_room`
--
ALTER TABLE `tbl_type_room`
  MODIFY `type_room_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=163;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
