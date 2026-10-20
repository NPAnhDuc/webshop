import { Category, Brand, Product, StrategicDocument, Promotion } from '../types/index.js';

export const INITIAL_CATEGORIES: Category[] = [
  {
    "id": "cat-case",
    "slug": "case",
    "name": "Vỏ Case"
  },
  {
    "id": "cat-cpu",
    "slug": "cpu",
    "name": "CPU - Vi xử lý"
  },
  {
    "id": "cat-ssd",
    "slug": "ssd",
    "name": "Ổ cứng SSD"
  },
  {
    "id": "cat-laptop",
    "slug": "laptop",
    "name": "Laptop"
  },
  {
    "id": "cat-ram",
    "slug": "ram",
    "name": "RAM - Bộ nhớ trong"
  },
  {
    "id": "cat-monitor",
    "slug": "monitor",
    "name": "Màn hình"
  },
  {
    "id": "cat-mainboard",
    "slug": "mainboard",
    "name": "Mainboard - Bo mạch chủ"
  },
  {
    "id": "cat-accessories",
    "slug": "accessories",
    "name": "Chuột & Phụ kiện"
  },
  {
    "id": "cat-psu",
    "slug": "psu",
    "name": "Nguồn máy tính PSU"
  },
  {
    "id": "cat-vga",
    "slug": "vga",
    "name": "Card đồ họa VGA"
  }
];

export const INITIAL_BRANDS: Brand[] = [
  {
    "id": "b-amd",
    "name": "AMD",
    "slug": "amd"
  },
  {
    "id": "b-aoc",
    "name": "AOC",
    "slug": "aoc"
  },
  {
    "id": "b-asus",
    "name": "ASUS",
    "slug": "asus"
  },
  {
    "id": "b-acer",
    "name": "Acer",
    "slug": "acer"
  },
  {
    "id": "b-apple",
    "name": "Apple",
    "slug": "apple"
  },
  {
    "id": "b-ch-nh-h-ng",
    "name": "Chính hãng",
    "slug": "ch-nh-h-ng"
  },
  {
    "id": "b-corsair",
    "name": "Corsair",
    "slug": "corsair"
  },
  {
    "id": "b-crucial",
    "name": "Crucial",
    "slug": "crucial"
  },
  {
    "id": "b-deepcool",
    "name": "Deepcool",
    "slug": "deepcool"
  },
  {
    "id": "b-dell",
    "name": "Dell",
    "slug": "dell"
  },
  {
    "id": "b-g-skill",
    "name": "G.Skill",
    "slug": "g-skill"
  },
  {
    "id": "b-gigabyte",
    "name": "Gigabyte",
    "slug": "gigabyte"
  },
  {
    "id": "b-hp",
    "name": "HP",
    "slug": "hp"
  },
  {
    "id": "b-intel",
    "name": "Intel",
    "slug": "intel"
  },
  {
    "id": "b-kingston",
    "name": "Kingston",
    "slug": "kingston"
  },
  {
    "id": "b-lenovo",
    "name": "Lenovo",
    "slug": "lenovo"
  },
  {
    "id": "b-logitech",
    "name": "Logitech",
    "slug": "logitech"
  },
  {
    "id": "b-msi",
    "name": "MSI",
    "slug": "msi"
  },
  {
    "id": "b-montech",
    "name": "Montech",
    "slug": "montech"
  },
  {
    "id": "b-nzxt",
    "name": "NZXT",
    "slug": "nzxt"
  },
  {
    "id": "b-razer",
    "name": "Razer",
    "slug": "razer"
  },
  {
    "id": "b-samsung",
    "name": "Samsung",
    "slug": "samsung"
  },
  {
    "id": "b-teamgroup",
    "name": "TEAMGROUP",
    "slug": "teamgroup"
  },
  {
    "id": "b-western-digital",
    "name": "Western Digital",
    "slug": "western-digital"
  }
];

export const INITIAL_PRODUCTS: Product[] = [
  {
    "id": "2c7e67b138aa88035c62b6dc52e8865156b2d3bb1e94a52887ddcf8466cea705",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-acer",
    "brandName": "Acer",
    "name": "Acer Aspire 3 A315-59-56VC",
    "slug": "acer-aspire-3-a315-59-56vc",
    "description": "Acer Aspire 3 A315-59-56VC chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 1235U mạnh mẽ",
      "Đồ họa Intel Iris Xe Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 12900000,
    "originalPrice": 14450000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-2c7e67b1-1",
        "productId": "2c7e67b138aa88035c62b6dc52e8865156b2d3bb1e94a52887ddcf8466cea705",
        "sku": "SKU-2C7E67B1",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 12900000,
        "originalPrice": 14450000,
        "costPrice": 11158000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 1235U",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel Iris Xe Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "aab3847c5592627507797bf6255ee692c94635cf2c51ba380cb276c5804022d0",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-acer",
    "brandName": "Acer",
    "name": "Acer Aspire 5 5P-A515-58P",
    "slug": "acer-aspire-5-5p-a515-58p",
    "description": "Acer Aspire 5 5P-A515-58P chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i3 1305U mạnh mẽ",
      "Đồ họa Intel UHD Graphics",
      "RAM 8GB DDR5 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/acer-aspire-5-5p-a515-58p-aab3847c5592.png",
    "images": [
      "/images/laptop/acer-aspire-5-5p-a515-58p-aab3847c5592.png"
    ],
    "price": 14900000,
    "originalPrice": 16690000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-aab3847c-1",
        "productId": "aab3847c5592627507797bf6255ee692c94635cf2c51ba380cb276c5804022d0",
        "sku": "SKU-AAB3847C",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14900000,
        "originalPrice": 16690000,
        "costPrice": 12888000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i3 1305U",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR5",
      "screen_inch": 15.6,
      "gpu_model": "Intel UHD Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "e8984ab22bacb81a6690709a3fa5edc1e754823e1b3b8b5549875f9c9b9993c8",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-acer",
    "brandName": "Acer",
    "name": "Acer Nitro 5 AN515-58-59JP",
    "slug": "acer-nitro-5-an515-58-59jp",
    "description": "Acer Nitro 5 AN515-58-59JP chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 12450H mạnh mẽ",
      "Đồ họa Nvidia RTX 3050 Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/acer-nitro-5-an515-58-59jp-e8984ab22bac.webp",
    "images": [
      "/images/laptop/acer-nitro-5-an515-58-59jp-e8984ab22bac.webp"
    ],
    "price": 18900000,
    "originalPrice": 21170000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-e8984ab2-1",
        "productId": "e8984ab22bacb81a6690709a3fa5edc1e754823e1b3b8b5549875f9c9b9993c8",
        "sku": "SKU-E8984AB2",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 18900000,
        "originalPrice": 21170000,
        "costPrice": 16348000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 12450H",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia RTX 3050 Graphics",
      "gpu_type": "discrete",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "0d1e921a974d5be9280c001db157bf593526b46d5599d752df06dfd7f4d8e3be",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-acer",
    "brandName": "Acer",
    "name": "Acer Swift Go 14 SFG14-41-R5RB",
    "slug": "acer-swift-go-14-sfg14-41-r5rb",
    "description": "Acer Swift Go 14 SFG14-41-R5RB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 14.0 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Ryzen 5 7530U mạnh mẽ",
      "Đồ họa AMD Radeon Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 15900000,
    "originalPrice": 17810000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-0d1e921a-1",
        "productId": "0d1e921a974d5be9280c001db157bf593526b46d5599d752df06dfd7f4d8e3be",
        "sku": "SKU-0D1E921A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 15900000,
        "originalPrice": 17810000,
        "costPrice": 13754000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Ryzen 5 7530U",
      "cpu_brand": "AMD",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 14.0,
      "gpu_model": "AMD Radeon Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 1
    }
  },
  {
    "id": "15bf0f5ed3d4ac16d4e624690beda50747bb516bf07c8a01c026f8a07da885fa",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-apple",
    "brandName": "Apple",
    "name": "Apple MacBook Air (Late 2020)",
    "slug": "apple-macbook-air-late-2020",
    "description": "Apple MacBook Air (Late 2020) chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 13.3 inch 2560x1600 sắc nét",
      "Bộ vi xử lý Apple M1 Chip mạnh mẽ",
      "Đồ họa Apple 7-core GPU",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/apple-macbook-air-late-2020-15bf0f5ed3d4.jpg",
    "images": [
      "/images/laptop/apple-macbook-air-late-2020-15bf0f5ed3d4.jpg"
    ],
    "price": 18900000,
    "originalPrice": 21170000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-15bf0f5e-1",
        "productId": "15bf0f5ed3d4ac16d4e624690beda50747bb516bf07c8a01c026f8a07da885fa",
        "sku": "SKU-15BF0F5E",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 18900000,
        "originalPrice": 21170000,
        "costPrice": 16348000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Apple M1 Chip",
      "cpu_brand": "Apple",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 13.3,
      "gpu_model": "Apple 7-core GPU",
      "gpu_type": "integrated",
      "resolution": "2560x1600",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "out_of_stock",
      "availableQty": 0
    }
  },
  {
    "id": "7910e2f35be3a42f108825bbf4cd8096f85c8b47bf52712c634b0f6812b257c2",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus TUF Gaming A15 FA506NF",
    "slug": "asus-tuf-gaming-a15-fa506nf",
    "description": "Asus TUF Gaming A15 FA506NF chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Ryzen 5 7535HS mạnh mẽ",
      "Đồ họa Nvidia RTX 2050 Graphics",
      "RAM 8GB DDR5 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/asus-tuf-gaming-a15-fa506nf-7910e2f35be3.jpg",
    "images": [
      "/images/laptop/asus-tuf-gaming-a15-fa506nf-7910e2f35be3.jpg"
    ],
    "price": 16500000,
    "originalPrice": 18480000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-7910e2f3-1",
        "productId": "7910e2f35be3a42f108825bbf4cd8096f85c8b47bf52712c634b0f6812b257c2",
        "sku": "SKU-7910E2F3",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 16500000,
        "originalPrice": 18480000,
        "costPrice": 14272000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Ryzen 5 7535HS",
      "cpu_brand": "AMD",
      "ram_gb": 8,
      "ram_type": "DDR5",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia RTX 2050 Graphics",
      "gpu_type": "discrete",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 1
    }
  },
  {
    "id": "ffaf140f9309bbce695b9e9e7fb77e48d436075a598b1685d32fb1e20d73ce50",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus VivoBook 15 X1500EA",
    "slug": "asus-vivobook-15-x1500ea",
    "description": "Asus VivoBook 15 X1500EA chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i3 1115G4 mạnh mẽ",
      "Đồ họa Intel UHD Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/asus-vivobook-15-x1500ea-ffaf140f9309.webp",
    "images": [
      "/images/laptop/asus-vivobook-15-x1500ea-ffaf140f9309.webp"
    ],
    "price": 13900000,
    "originalPrice": 15570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-ffaf140f-1",
        "productId": "ffaf140f9309bbce695b9e9e7fb77e48d436075a598b1685d32fb1e20d73ce50",
        "sku": "SKU-FFAF140F",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 13900000,
        "originalPrice": 15570000,
        "costPrice": 12024000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i3 1115G4",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel UHD Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "675dc82b5a646a467ee8700a0996d29f087df0ffb7ee41334bdf1290338534fc",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus ZenBook 14 UM425UA",
    "slug": "asus-zenbook-14-um425ua",
    "description": "Asus ZenBook 14 UM425UA chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 14.0 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Ryzen 5 5500U mạnh mẽ",
      "Đồ họa AMD Radeon Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/asus-zenbook-14-um425ua-675dc82b5a64.png",
    "images": [
      "/images/laptop/asus-zenbook-14-um425ua-675dc82b5a64.png"
    ],
    "price": 14900000,
    "originalPrice": 16690000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-675dc82b-1",
        "productId": "675dc82b5a646a467ee8700a0996d29f087df0ffb7ee41334bdf1290338534fc",
        "sku": "SKU-675DC82B",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14900000,
        "originalPrice": 16690000,
        "costPrice": 12888000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Ryzen 5 5500U",
      "cpu_brand": "AMD",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 14.0,
      "gpu_model": "AMD Radeon Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "beb1ccb3c40ba232bccce21f6e97956fdb6bad33b34d20d86d1afbe5624e9090",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-dell",
    "brandName": "Dell",
    "name": "Dell Inspiron 15 3520",
    "slug": "dell-inspiron-15-3520",
    "description": "Dell Inspiron 15 3520 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i3 1215U mạnh mẽ",
      "Đồ họa Intel UHD Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/dell-inspiron-15-3520-beb1ccb3c40b.jpg",
    "images": [
      "/images/laptop/dell-inspiron-15-3520-beb1ccb3c40b.jpg"
    ],
    "price": 13900000,
    "originalPrice": 15570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-beb1ccb3-1",
        "productId": "beb1ccb3c40ba232bccce21f6e97956fdb6bad33b34d20d86d1afbe5624e9090",
        "sku": "SKU-BEB1CCB3",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 13900000,
        "originalPrice": 15570000,
        "costPrice": 12024000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i3 1215U",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel UHD Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "a593b00374e32cd9fd04a8e0be87a9e4892d6d60c0b708f811ea5aaee5dd55d6",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-dell",
    "brandName": "Dell",
    "name": "Dell Latitude 3430",
    "slug": "dell-latitude-3430",
    "description": "Dell Latitude 3430 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 14.0 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i3 1215U mạnh mẽ",
      "Đồ họa Intel UHD Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 15500000,
    "originalPrice": 17360000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-a593b003-1",
        "productId": "a593b00374e32cd9fd04a8e0be87a9e4892d6d60c0b708f811ea5aaee5dd55d6",
        "sku": "SKU-A593B003",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 15500000,
        "originalPrice": 17360000,
        "costPrice": 13408000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i3 1215U",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 14.0,
      "gpu_model": "Intel UHD Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "4d3639044079fed27125c056d8db4cf5acd911b187dc3496322cf772275a7092",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-dell",
    "brandName": "Dell",
    "name": "Dell Vostro 15 3510",
    "slug": "dell-vostro-15-3510",
    "description": "Dell Vostro 15 3510 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 1135G7 mạnh mẽ",
      "Đồ họa Nvidia MX330 Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 13500000,
    "originalPrice": 15120000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-4d363904-1",
        "productId": "4d3639044079fed27125c056d8db4cf5acd911b187dc3496322cf772275a7092",
        "sku": "SKU-4D363904",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 13500000,
        "originalPrice": 15120000,
        "costPrice": 11678000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 1135G7",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia MX330 Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 1
    }
  },
  {
    "id": "8e9bc75a15e9ae5c7d0c72f6e1201c76b3dc852c945e7422a2f999ead68b7605",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-gigabyte",
    "brandName": "Gigabyte",
    "name": "Gigabyte Gaming G5 MF",
    "slug": "gigabyte-gaming-g5-mf",
    "description": "Gigabyte Gaming G5 MF chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 12500H mạnh mẽ",
      "Đồ họa Nvidia RTX 4050 Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 21900000,
    "originalPrice": 24530000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-8e9bc75a-1",
        "productId": "8e9bc75a15e9ae5c7d0c72f6e1201c76b3dc852c945e7422a2f999ead68b7605",
        "sku": "SKU-8E9BC75A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 21900000,
        "originalPrice": 24530000,
        "costPrice": 18944000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 12500H",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia RTX 4050 Graphics",
      "gpu_type": "discrete",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "918991685e362df8f799e996de2c3ec56fd9b8026a6fc4da5f39bb7757f239d5",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-hp",
    "brandName": "HP",
    "name": "HP 15-fd0202TU",
    "slug": "hp-15-fd0202tu",
    "description": "HP 15-fd0202TU chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 1335U mạnh mẽ",
      "Đồ họa Intel Iris Xe Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 15500000,
    "originalPrice": 17360000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-91899168-1",
        "productId": "918991685e362df8f799e996de2c3ec56fd9b8026a6fc4da5f39bb7757f239d5",
        "sku": "SKU-91899168",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 15500000,
        "originalPrice": 17360000,
        "costPrice": 13408000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 1335U",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel Iris Xe Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "4dd041b2a1a087f7010dd3af5b464345c922cf6ef87104281ec028cdcea7e22c",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-hp",
    "brandName": "HP",
    "name": "HP Victus Gaming 15-fa1251TX",
    "slug": "hp-victus-gaming-15-fa1251tx",
    "description": "HP Victus Gaming 15-fa1251TX chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i7 13700H mạnh mẽ",
      "Đồ họa Nvidia RTX 3050 Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/hp-victus-gaming-15-fa1251tx-4dd041b2a1a0.webp",
    "images": [
      "/images/laptop/hp-victus-gaming-15-fa1251tx-4dd041b2a1a0.webp"
    ],
    "price": 19900000,
    "originalPrice": 22290000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-4dd041b2-1",
        "productId": "4dd041b2a1a087f7010dd3af5b464345c922cf6ef87104281ec028cdcea7e22c",
        "sku": "SKU-4DD041B2",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 19900000,
        "originalPrice": 22290000,
        "costPrice": 17214000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i7 13700H",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia RTX 3050 Graphics",
      "gpu_type": "discrete",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "01eec94bf55b77e191c4185e53a67d1e132371664fc9b310e12bcec0c88d9a1c",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-lenovo",
    "brandName": "Lenovo",
    "name": "Lenovo IdeaPad Slim 3i 15ITL6",
    "slug": "lenovo-ideapad-slim-3i-15itl6",
    "description": "Lenovo IdeaPad Slim 3i 15ITL6 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i7 1165G7 mạnh mẽ",
      "Đồ họa Intel Iris Xe Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-ideapad-slim-3i-15itl6-01eec94bf55b.webp",
    "images": [
      "/images/laptop/lenovo-ideapad-slim-3i-15itl6-01eec94bf55b.webp"
    ],
    "price": 13500000,
    "originalPrice": 15120000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-01eec94b-1",
        "productId": "01eec94bf55b77e191c4185e53a67d1e132371664fc9b310e12bcec0c88d9a1c",
        "sku": "SKU-01EEC94B",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 13500000,
        "originalPrice": 15120000,
        "costPrice": 11678000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i7 1165G7",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel Iris Xe Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "68999d66ddb777cb061ce852f404dd944df76cd8b088ff5da57d1b020f769b33",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-lenovo",
    "brandName": "Lenovo",
    "name": "Lenovo LOQ Gaming 15IRH8",
    "slug": "lenovo-loq-gaming-15irh8",
    "description": "Lenovo LOQ Gaming 15IRH8 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 12450H mạnh mẽ",
      "Đồ họa Nvidia RTX 2050 Graphics",
      "RAM 16GB DDR5 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 17500000,
    "originalPrice": 19600000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-68999d66-1",
        "productId": "68999d66ddb777cb061ce852f404dd944df76cd8b088ff5da57d1b020f769b33",
        "sku": "SKU-68999D66",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 17500000,
        "originalPrice": 19600000,
        "costPrice": 15138000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 12450H",
      "cpu_brand": "Intel",
      "ram_gb": 16,
      "ram_type": "DDR5",
      "screen_inch": 15.6,
      "gpu_model": "Nvidia RTX 2050 Graphics",
      "gpu_type": "discrete",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "7bf3496c4c551140ad0ba93210771103268de54e0ffca4c389c650ed3acd8fbf",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-lenovo",
    "brandName": "Lenovo",
    "name": "Lenovo Legion Slim 5i 16IRH8",
    "slug": "lenovo-legion-slim-5i-16irh8",
    "description": "Lenovo Legion Slim 5i 16IRH8 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 16.0 inch 2560x1600 sắc nét",
      "Bộ vi xử lý Core i5 13500H mạnh mẽ",
      "Đồ họa Nvidia RTX 4050 Graphics",
      "RAM 16GB DDR5 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-legion-slim-5i-16irh8-7bf3496c4c55.png",
    "images": [
      "/images/laptop/lenovo-legion-slim-5i-16irh8-7bf3496c4c55.png"
    ],
    "price": 26000000,
    "originalPrice": 29120000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-7bf3496c-1",
        "productId": "7bf3496c4c551140ad0ba93210771103268de54e0ffca4c389c650ed3acd8fbf",
        "sku": "SKU-7BF3496C",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 26000000,
        "originalPrice": 29120000,
        "costPrice": 22490000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 13500H",
      "cpu_brand": "Intel",
      "ram_gb": 16,
      "ram_type": "DDR5",
      "screen_inch": 16.0,
      "gpu_model": "Nvidia RTX 4050 Graphics",
      "gpu_type": "discrete",
      "resolution": "2560x1600",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "gaming",
        "design_graphics"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "9d2cf777d54302b4c0a7f3d0f4f0866b441a3af2de79dd4bb91bf1de5ae99f35",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-lenovo",
    "brandName": "Lenovo",
    "name": "Lenovo ThinkBook 15 G2 ITL",
    "slug": "lenovo-thinkbook-15-g2-itl",
    "description": "Lenovo ThinkBook 15 G2 ITL chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i5 1135G7 mạnh mẽ",
      "Đồ họa Intel Iris Xe Graphics",
      "RAM 8GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 14500000,
    "originalPrice": 16240000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-9d2cf777-1",
        "productId": "9d2cf777d54302b4c0a7f3d0f4f0866b441a3af2de79dd4bb91bf1de5ae99f35",
        "sku": "SKU-9D2CF777",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14500000,
        "originalPrice": 16240000,
        "costPrice": 12542000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i5 1135G7",
      "cpu_brand": "Intel",
      "ram_gb": 8,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel Iris Xe Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 1
    }
  },
  {
    "id": "2243d61cc7fbfde1c3d93d38a133c97a6edb6b1d950fca079a016c91c049a5f1",
    "categoryId": "cat-laptop",
    "categorySlug": "laptop",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI Modern 15 B12M",
    "slug": "msi-modern-15-b12m",
    "description": "MSI Modern 15 B12M chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Màn hình 15.6 inch 1920x1080 sắc nét",
      "Bộ vi xử lý Core i7 1255U mạnh mẽ",
      "Đồ họa Intel Iris Xe Graphics",
      "RAM 16GB DDR4 & SSD 512GB NVMe tốc độ cao"
    ],
    "imageUrl": "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png",
    "images": [
      "/images/laptop/lenovo-loq-gaming-15irh8-68999d66ddb7.png"
    ],
    "price": 14500000,
    "originalPrice": 16240000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-2243d61c-1",
        "productId": "2243d61cc7fbfde1c3d93d38a133c97a6edb6b1d950fca079a016c91c049a5f1",
        "sku": "SKU-2243D61C",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14500000,
        "originalPrice": 16240000,
        "costPrice": 12542000,
        "status": "active"
      }
    ],
    "specs": {
      "cpu_model": "Core i7 1255U",
      "cpu_brand": "Intel",
      "ram_gb": 16,
      "ram_type": "DDR4",
      "screen_inch": 15.6,
      "gpu_model": "Intel Iris Xe Graphics",
      "gpu_type": "integrated",
      "resolution": "1920x1080",
      "panel": "IPS",
      "storage_gb": 512,
      "storage_type": "NVMe",
      "warranty_months": 24,
      "demand": [
        "study_office",
        "thin_light"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 1
    }
  },
  {
    "id": "a8126e19618722d49b8b39daf606b809c3b3e9d657ac4b8c63ca4a31122fde17",
    "categoryId": "cat-accessories",
    "categorySlug": "accessories",
    "brandId": "b-logitech",
    "brandName": "Logitech",
    "name": "Logitech G305 LIGHTSPEED",
    "slug": "logitech-g305-lightspeed",
    "description": "Logitech G305 LIGHTSPEED chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Cảm biến quang học chính xác cao",
      "Kết nối độ trễ siêu thấp",
      "Thiết kế công thái học nhẹ nhàng"
    ],
    "imageUrl": "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg",
    "images": [
      "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg"
    ],
    "price": 760000,
    "originalPrice": 850000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-a8126e19-1",
        "productId": "a8126e19618722d49b8b39daf606b809c3b3e9d657ac4b8c63ca4a31122fde17",
        "sku": "SKU-A8126E19",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 760000,
        "originalPrice": 850000,
        "costPrice": 517000,
        "status": "active"
      }
    ],
    "specs": {},
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "5935e8da7b96afb4f7abfab7d90e678673e16f3dc8d7cde6e563c7ed0697df36",
    "categoryId": "cat-accessories",
    "categorySlug": "accessories",
    "brandId": "b-logitech",
    "brandName": "Logitech",
    "name": "Logitech G502 Hero",
    "slug": "logitech-g502-hero",
    "description": "Logitech G502 Hero chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Cảm biến quang học chính xác cao",
      "Kết nối độ trễ siêu thấp",
      "Thiết kế công thái học nhẹ nhàng"
    ],
    "imageUrl": "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg",
    "images": [
      "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg"
    ],
    "price": 1110000,
    "originalPrice": 1240000,
    "discountPercent": 10,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-5935e8da-1",
        "productId": "5935e8da7b96afb4f7abfab7d90e678673e16f3dc8d7cde6e563c7ed0697df36",
        "sku": "SKU-5935E8DA",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1110000,
        "originalPrice": 1240000,
        "costPrice": 755000,
        "status": "active"
      }
    ],
    "specs": {},
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "a2f8c8d487a673677719cfe7ecacd408dcfea090123d6ef31321a67bdf83cb78",
    "categoryId": "cat-accessories",
    "categorySlug": "accessories",
    "brandId": "b-razer",
    "brandName": "Razer",
    "name": "Razer Basilisk V3",
    "slug": "razer-basilisk-v3",
    "description": "Razer Basilisk V3 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Cảm biến quang học chính xác cao",
      "Kết nối độ trễ siêu thấp",
      "Thiết kế công thái học nhẹ nhàng"
    ],
    "imageUrl": "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg",
    "images": [
      "/images/mouse/logitech-g305-lightspeed-a8126e196187.jpg"
    ],
    "price": 1040000,
    "originalPrice": 1160000,
    "discountPercent": 10,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-a2f8c8d4-1",
        "productId": "a2f8c8d487a673677719cfe7ecacd408dcfea090123d6ef31321a67bdf83cb78",
        "sku": "SKU-A2F8C8D4",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1040000,
        "originalPrice": 1160000,
        "costPrice": 707000,
        "status": "active"
      }
    ],
    "specs": {},
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "95a534457590f6c18dea18ccbf2f99caa583b2f99c73cae3b7f5816b15ecf850",
    "categoryId": "cat-accessories",
    "categorySlug": "accessories",
    "brandId": "b-razer",
    "brandName": "Razer",
    "name": "Razer DeathAdder Essential",
    "slug": "razer-deathadder-essential",
    "description": "Razer DeathAdder Essential chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Cảm biến quang học chính xác cao",
      "Kết nối độ trễ siêu thấp",
      "Thiết kế công thái học nhẹ nhàng"
    ],
    "imageUrl": "/images/mouse/razer-deathadder-essential-95a534457590.png",
    "images": [
      "/images/mouse/razer-deathadder-essential-95a534457590.png"
    ],
    "price": 510000,
    "originalPrice": 570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-95a53445-1",
        "productId": "95a534457590f6c18dea18ccbf2f99caa583b2f99c73cae3b7f5816b15ecf850",
        "sku": "SKU-95A53445",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 510000,
        "originalPrice": 570000,
        "costPrice": 347000,
        "status": "active"
      }
    ],
    "specs": {},
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "349a9bcb6e003baee5b28124c6d755ef4c51d12df241ed8bddf0127f9af0c9f6",
    "categoryId": "cat-case",
    "categorySlug": "case",
    "brandId": "b-corsair",
    "brandName": "Corsair",
    "name": "Corsair 4000D Airflow",
    "slug": "corsair-4000d-airflow",
    "description": "Corsair 4000D Airflow chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ bo mạch chủ ATX, Micro-ATX, Mini-ITX",
      "Mặt kính cường lực cao cấp, tối ưu luồng gió Airflow",
      "Không gian rộng rãi lắp card đồ họa dài tới 360mm"
    ],
    "imageUrl": "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg",
    "images": [
      "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg"
    ],
    "price": 2500000,
    "originalPrice": 2800000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-349a9bcb-1",
        "productId": "349a9bcb6e003baee5b28124c6d755ef4c51d12df241ed8bddf0127f9af0c9f6",
        "sku": "SKU-349A9BCB",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2500000,
        "originalPrice": 2800000,
        "costPrice": 1875000,
        "status": "active"
      }
    ],
    "specs": {
      "supported_form_factors": [
        "ATX",
        "mATX",
        "ITX"
      ],
      "max_gpu_length_mm": 360,
      "max_cooler_height_mm": 170
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "b2a5e436f83c19404871a6aa2836c544e4dba5021c50b43d7ec78f273f3db171",
    "categoryId": "cat-case",
    "categorySlug": "case",
    "brandId": "b-deepcool",
    "brandName": "Deepcool",
    "name": "Deepcool CH160",
    "slug": "deepcool-ch160",
    "description": "Deepcool CH160 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ bo mạch chủ ATX, Micro-ATX, Mini-ITX",
      "Mặt kính cường lực cao cấp, tối ưu luồng gió Airflow",
      "Không gian rộng rãi lắp card đồ họa dài tới 360mm"
    ],
    "imageUrl": "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg",
    "images": [
      "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg"
    ],
    "price": 2170000,
    "originalPrice": 2430000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-b2a5e436-1",
        "productId": "b2a5e436f83c19404871a6aa2836c544e4dba5021c50b43d7ec78f273f3db171",
        "sku": "SKU-B2A5E436",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2170000,
        "originalPrice": 2430000,
        "costPrice": 1628000,
        "status": "active"
      }
    ],
    "specs": {
      "supported_form_factors": [
        "ATX",
        "mATX",
        "ITX"
      ],
      "max_gpu_length_mm": 360,
      "max_cooler_height_mm": 170
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "21e32cbca4b2a85c6550e75b0e2aecf5d666af461cb946e5f94f9833dc3247ca",
    "categoryId": "cat-case",
    "categorySlug": "case",
    "brandId": "b-montech",
    "brandName": "Montech",
    "name": "Montech AIR 903 MAX",
    "slug": "montech-air-903-max",
    "description": "Montech AIR 903 MAX chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ bo mạch chủ ATX, Micro-ATX, Mini-ITX",
      "Mặt kính cường lực cao cấp, tối ưu luồng gió Airflow",
      "Không gian rộng rãi lắp card đồ họa dài tới 360mm"
    ],
    "imageUrl": "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg",
    "images": [
      "/images/case/corsair-4000d-airflow-349a9bcb6e00.jpg"
    ],
    "price": 1990000,
    "originalPrice": 2230000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-21e32cbc-1",
        "productId": "21e32cbca4b2a85c6550e75b0e2aecf5d666af461cb946e5f94f9833dc3247ca",
        "sku": "SKU-21E32CBC",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1990000,
        "originalPrice": 2230000,
        "costPrice": 1492000,
        "status": "active"
      }
    ],
    "specs": {
      "supported_form_factors": [
        "ATX",
        "mATX",
        "ITX"
      ],
      "max_gpu_length_mm": 360,
      "max_cooler_height_mm": 170
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "6d80f639a0901679845ecc8e6c0b895d6e47f7aca628afe12b64cc06ca119438",
    "categoryId": "cat-case",
    "categorySlug": "case",
    "brandId": "b-nzxt",
    "brandName": "NZXT",
    "name": "NZXT H5 Flow (2024)",
    "slug": "nzxt-h5-flow-2024",
    "description": "NZXT H5 Flow (2024) chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ bo mạch chủ ATX, Micro-ATX, Mini-ITX",
      "Mặt kính cường lực cao cấp, tối ưu luồng gió Airflow",
      "Không gian rộng rãi lắp card đồ họa dài tới 360mm"
    ],
    "imageUrl": "/images/case/nzxt-h5-flow-2024-6d80f639a090.jpg",
    "images": [
      "/images/case/nzxt-h5-flow-2024-6d80f639a090.jpg"
    ],
    "price": 2130000,
    "originalPrice": 2390000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-6d80f639-1",
        "productId": "6d80f639a0901679845ecc8e6c0b895d6e47f7aca628afe12b64cc06ca119438",
        "sku": "SKU-6D80F639",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2130000,
        "originalPrice": 2390000,
        "costPrice": 1598000,
        "status": "active"
      }
    ],
    "specs": {
      "supported_form_factors": [
        "ATX",
        "mATX",
        "ITX"
      ],
      "max_gpu_length_mm": 360,
      "max_cooler_height_mm": 170
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "c9ab253a5d81db91a15166655f5abdfad3fcf5210f55424a67e41111296e620f",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-amd",
    "brandName": "AMD",
    "name": "AMD Ryzen 5 7600X",
    "slug": "amd-ryzen-5-7600x",
    "description": "AMD Ryzen 5 7600X chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket AM5, công suất TDP 105W",
      "Số nhân xử lý: 6 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-5-7600x-c9ab253a5d81.webp",
    "images": [
      "/images/cpu/amd-ryzen-5-7600x-c9ab253a5d81.webp"
    ],
    "price": 4090000,
    "originalPrice": 4580000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-c9ab253a-1",
        "productId": "c9ab253a5d81db91a15166655f5abdfad3fcf5210f55424a67e41111296e620f",
        "sku": "SKU-C9AB253A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 4090000,
        "originalPrice": 4580000,
        "costPrice": 3436000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "cores": 6,
      "tdp_w": 105,
      "has_igpu": true
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "c13cde96e5406b28de88c10bf92d71134cd12fef6c99f486bbb7781f9df6ddc9",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-amd",
    "brandName": "AMD",
    "name": "AMD Ryzen 5 9600X",
    "slug": "amd-ryzen-5-9600x",
    "description": "AMD Ryzen 5 9600X chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket AM5, công suất TDP 65W",
      "Số nhân xử lý: 6 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg",
    "images": [
      "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg"
    ],
    "price": 5400000,
    "originalPrice": 6050000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-c13cde96-1",
        "productId": "c13cde96e5406b28de88c10bf92d71134cd12fef6c99f486bbb7781f9df6ddc9",
        "sku": "SKU-C13CDE96",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 5400000,
        "originalPrice": 6050000,
        "costPrice": 4536000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "cores": 6,
      "tdp_w": 65,
      "has_igpu": true
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "4f18cab5f769b246ad783f9473bd6eed6a2899092dd3e42de4b8fb31d0cb9c78",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-amd",
    "brandName": "AMD",
    "name": "AMD Ryzen 7 5700X3D",
    "slug": "amd-ryzen-7-5700x3d",
    "description": "AMD Ryzen 7 5700X3D chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket AM5, công suất TDP 105W",
      "Số nhân xử lý: 8 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg",
    "images": [
      "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg"
    ],
    "price": 7800000,
    "originalPrice": 8740000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-4f18cab5-1",
        "productId": "4f18cab5f769b246ad783f9473bd6eed6a2899092dd3e42de4b8fb31d0cb9c78",
        "sku": "SKU-4F18CAB5",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 7800000,
        "originalPrice": 8740000,
        "costPrice": 6552000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "cores": 8,
      "tdp_w": 105,
      "has_igpu": true
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "a42c71398b07e30bd31f842b62b64ba322bf521e7dea0c8bd19fbde112f3869e",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-amd",
    "brandName": "AMD",
    "name": "AMD Ryzen 7 7700X",
    "slug": "amd-ryzen-7-7700x",
    "description": "AMD Ryzen 7 7700X chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket AM5, công suất TDP 105W",
      "Số nhân xử lý: 8 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg",
    "images": [
      "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg"
    ],
    "price": 6400000,
    "originalPrice": 7170000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-a42c7139-1",
        "productId": "a42c71398b07e30bd31f842b62b64ba322bf521e7dea0c8bd19fbde112f3869e",
        "sku": "SKU-A42C7139",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 6400000,
        "originalPrice": 7170000,
        "costPrice": 5376000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "cores": 8,
      "tdp_w": 105,
      "has_igpu": true
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "20627684ea0548ecdaef1e6d76270b0e9c733c5c4ea267c4a099c8832f4c3215",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-amd",
    "brandName": "AMD",
    "name": "AMD Ryzen 7 9800X3D",
    "slug": "amd-ryzen-7-9800x3d",
    "description": "AMD Ryzen 7 9800X3D chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket AM5, công suất TDP 120W",
      "Số nhân xử lý: 8 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg",
    "images": [
      "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg"
    ],
    "price": 10950000,
    "originalPrice": 12260000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-20627684-1",
        "productId": "20627684ea0548ecdaef1e6d76270b0e9c733c5c4ea267c4a099c8832f4c3215",
        "sku": "SKU-20627684",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 10950000,
        "originalPrice": 12260000,
        "costPrice": 9198000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "cores": 8,
      "tdp_w": 120,
      "has_igpu": true
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "7719e96537610f3d2ae0fac067c7809bcbca00d7b7c13b69099130fe73992cb4",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-intel",
    "brandName": "Intel",
    "name": "Intel Core i5-12400F",
    "slug": "intel-core-i5-12400f",
    "description": "Intel Core i5-12400F chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket LGA1700, công suất TDP 65W",
      "Số nhân xử lý: 6 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/intel-core-i5-12400f-7719e9653761.jpg",
    "images": [
      "/images/cpu/intel-core-i5-12400f-7719e9653761.jpg"
    ],
    "price": 3020000,
    "originalPrice": 3380000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-7719e965-1",
        "productId": "7719e96537610f3d2ae0fac067c7809bcbca00d7b7c13b69099130fe73992cb4",
        "sku": "SKU-7719E965",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3020000,
        "originalPrice": 3380000,
        "costPrice": 2537000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "LGA1700",
      "cores": 6,
      "tdp_w": 65,
      "has_igpu": false
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "37519dda6cf19f177d3952b4f6ccfbb1edeac669bbb3734536315de55ecfc6fb",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-intel",
    "brandName": "Intel",
    "name": "Intel Core i5-14400F",
    "slug": "intel-core-i5-14400f",
    "description": "Intel Core i5-14400F chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket LGA1700, công suất TDP 65W",
      "Số nhân xử lý: 10 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/intel-core-i5-14400f-37519dda6cf1.jpg",
    "images": [
      "/images/cpu/intel-core-i5-14400f-37519dda6cf1.jpg"
    ],
    "price": 3190000,
    "originalPrice": 3570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-37519dda-1",
        "productId": "37519dda6cf19f177d3952b4f6ccfbb1edeac669bbb3734536315de55ecfc6fb",
        "sku": "SKU-37519DDA",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3190000,
        "originalPrice": 3570000,
        "costPrice": 2680000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "LGA1700",
      "cores": 10,
      "tdp_w": 65,
      "has_igpu": false
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "8e9a39cee3d830394b4f3114061a0cb40eb49af4ec79bf91dacc2eef94e3c084",
    "categoryId": "cat-cpu",
    "categorySlug": "cpu",
    "brandId": "b-intel",
    "brandName": "Intel",
    "name": "Intel Core i5-14600KF",
    "slug": "intel-core-i5-14600kf",
    "description": "Intel Core i5-14600KF chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Socket LGA1700, công suất TDP 125W",
      "Số nhân xử lý: 14 nhân đa nhiệm vượt trội",
      "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
    ],
    "imageUrl": "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg",
    "images": [
      "/images/cpu/amd-ryzen-7-9800x3d-20627684ea05.jpg"
    ],
    "price": 4940000,
    "originalPrice": 5530000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-8e9a39ce-1",
        "productId": "8e9a39cee3d830394b4f3114061a0cb40eb49af4ec79bf91dacc2eef94e3c084",
        "sku": "SKU-8E9A39CE",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 4940000,
        "originalPrice": 5530000,
        "costPrice": 4150000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "LGA1700",
      "cores": 14,
      "tdp_w": 125,
      "has_igpu": false
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "6eb51f4a845a42d927919d341984360495448ada42f55ef7d5870e6b5f333972",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus PRIME B550M-A WIFI II",
    "slug": "asus-prime-b550m-a-wifi-ii",
    "description": "Asus PRIME B550M-A WIFI II chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket AM4 chuẩn mATX",
      "Hỗ trợ RAM DDR4 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/asus-prime-b550m-a-wifi-ii-6eb51f4a845a.png",
    "images": [
      "/images/motherboard/asus-prime-b550m-a-wifi-ii-6eb51f4a845a.png"
    ],
    "price": 2640000,
    "originalPrice": 2960000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-6eb51f4a-1",
        "productId": "6eb51f4a845a42d927919d341984360495448ada42f55ef7d5870e6b5f333972",
        "sku": "SKU-6EB51F4A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2640000,
        "originalPrice": 2960000,
        "costPrice": 2138000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM4",
      "form_factor": "mATX",
      "ram_type": "DDR4",
      "ram_slots": 4,
      "supported_form_factors": [
        "mATX"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "c6488d4e841b7392e018b629fdd6b8c8ce461577492399eef5b7cb292af86aa6",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus PRIME B650-PLUS WIFI",
    "slug": "asus-prime-b650-plus-wifi",
    "description": "Asus PRIME B650-PLUS WIFI chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket AM5 chuẩn ATX",
      "Hỗ trợ RAM DDR5 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png",
    "images": [
      "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png"
    ],
    "price": 4270000,
    "originalPrice": 4780000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-c6488d4e-1",
        "productId": "c6488d4e841b7392e018b629fdd6b8c8ce461577492399eef5b7cb292af86aa6",
        "sku": "SKU-C6488D4E",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 4270000,
        "originalPrice": 4780000,
        "costPrice": 3459000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "form_factor": "ATX",
      "ram_type": "DDR5",
      "ram_slots": 4,
      "supported_form_factors": [
        "ATX"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "7ac8293143f64b96e17d87991c1b33ff6a850b5d8a7a8c75e9bb2ed3524c7b3d",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus TUF GAMING B850-PLUS WIFI",
    "slug": "asus-tuf-gaming-b850-plus-wifi",
    "description": "Asus TUF GAMING B850-PLUS WIFI chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket AM5 chuẩn ATX",
      "Hỗ trợ RAM DDR5 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/asus-tuf-gaming-b850-plus-wifi-7ac8293143f6.jpg",
    "images": [
      "/images/motherboard/asus-tuf-gaming-b850-plus-wifi-7ac8293143f6.jpg"
    ],
    "price": 6080000,
    "originalPrice": 6810000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-7ac82931-1",
        "productId": "7ac8293143f64b96e17d87991c1b33ff6a850b5d8a7a8c75e9bb2ed3524c7b3d",
        "sku": "SKU-7AC82931",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 6080000,
        "originalPrice": 6810000,
        "costPrice": 4925000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM5",
      "form_factor": "ATX",
      "ram_type": "DDR5",
      "ram_slots": 4,
      "supported_form_factors": [
        "ATX"
      ]
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "3306789bd8e6247c1b5adae63310a4811a68177bcf53e8ad75a8d637d2c0e5a2",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-gigabyte",
    "brandName": "Gigabyte",
    "name": "Gigabyte X870E AORUS ELITE WIFI7",
    "slug": "gigabyte-x870e-aorus-elite-wifi7",
    "description": "Gigabyte X870E AORUS ELITE WIFI7 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket AM4 chuẩn ATX",
      "Hỗ trợ RAM DDR4 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png",
    "images": [
      "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png"
    ],
    "price": 8380000,
    "originalPrice": 9390000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-3306789b-1",
        "productId": "3306789bd8e6247c1b5adae63310a4811a68177bcf53e8ad75a8d637d2c0e5a2",
        "sku": "SKU-3306789B",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 8380000,
        "originalPrice": 9390000,
        "costPrice": 6788000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "AM4",
      "form_factor": "ATX",
      "ram_type": "DDR4",
      "ram_slots": 4,
      "supported_form_factors": [
        "ATX"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "ee2d7931b81ddeaeb317d9e95d25217653675002f1d27ad1719734052a4797e8",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI B760 GAMING PLUS WIFI",
    "slug": "msi-b760-gaming-plus-wifi",
    "description": "MSI B760 GAMING PLUS WIFI chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket LGA1700 chuẩn ATX",
      "Hỗ trợ RAM DDR5 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/msi-b760-gaming-plus-wifi-ee2d7931b81d.jpg",
    "images": [
      "/images/motherboard/msi-b760-gaming-plus-wifi-ee2d7931b81d.jpg"
    ],
    "price": 4110000,
    "originalPrice": 4600000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-ee2d7931-1",
        "productId": "ee2d7931b81ddeaeb317d9e95d25217653675002f1d27ad1719734052a4797e8",
        "sku": "SKU-EE2D7931",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 4110000,
        "originalPrice": 4600000,
        "costPrice": 3329000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "LGA1700",
      "form_factor": "ATX",
      "ram_type": "DDR5",
      "ram_slots": 4,
      "supported_form_factors": [
        "ATX"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "42f61174b59c43fd77aa7d75619043621dafb8d759f6091a61bfdcfea5d517bd",
    "categoryId": "cat-mainboard",
    "categorySlug": "mainboard",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI PRO Z790-A MAX WIFI",
    "slug": "msi-pro-z790-a-max-wifi",
    "description": "MSI PRO Z790-A MAX WIFI chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Hỗ trợ CPU Socket LGA1700 chuẩn ATX",
      "Hỗ trợ RAM DDR5 tốc độ cao với 4 khe cắm",
      "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
    ],
    "imageUrl": "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png",
    "images": [
      "/images/motherboard/asus-prime-b650-plus-wifi-c6488d4e841b.png"
    ],
    "price": 5430000,
    "originalPrice": 6080000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-42f61174-1",
        "productId": "42f61174b59c43fd77aa7d75619043621dafb8d759f6091a61bfdcfea5d517bd",
        "sku": "SKU-42F61174",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 5430000,
        "originalPrice": 6080000,
        "costPrice": 4398000,
        "status": "active"
      }
    ],
    "specs": {
      "socket": "LGA1700",
      "form_factor": "ATX",
      "ram_type": "DDR5",
      "ram_slots": 4,
      "supported_form_factors": [
        "ATX"
      ]
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "a0778acc1ac59c3e48b63cbca76375857326f43f2069d3f06a7f3eebbc7b4a12",
    "categoryId": "cat-monitor",
    "categorySlug": "monitor",
    "brandId": "b-aoc",
    "brandName": "AOC",
    "name": "AOC 24G4XE",
    "slug": "aoc-24g4xe",
    "description": "AOC 24G4XE chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Kích thước 24 inch độ phân giải 1920 x 1080 (FHD)",
      "Tần số quét cao 180Hz chuyên game mượt mà",
      "Tấm nền IPS góc nhìn rộng 178 độ chuẩn màu"
    ],
    "imageUrl": "/images/monitor/aoc-24g4xe-a0778acc1ac5.png",
    "images": [
      "/images/monitor/aoc-24g4xe-a0778acc1ac5.png"
    ],
    "price": 6250000,
    "originalPrice": 7000000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-a0778acc-1",
        "productId": "a0778acc1ac59c3e48b63cbca76375857326f43f2069d3f06a7f3eebbc7b4a12",
        "sku": "SKU-A0778ACC",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 6250000,
        "originalPrice": 7000000,
        "costPrice": 5125000,
        "status": "active"
      }
    ],
    "specs": {
      "screen_inch": 24,
      "panel": "IPS",
      "refresh_hz": 180,
      "resolution": "1920 x 1080 (FHD)"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "80c7806acde7949635c084a5fa6fcdf20a0dd8816d86fa7c56f59a5e4be6738f",
    "categoryId": "cat-monitor",
    "categorySlug": "monitor",
    "brandId": "b-asus",
    "brandName": "ASUS",
    "name": "Asus TUF Gaming VG27AQ",
    "slug": "asus-tuf-gaming-vg27aq",
    "description": "Asus TUF Gaming VG27AQ chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Kích thước 27 inch độ phân giải 2560 x 1440 (2K)",
      "Tần số quét cao 165Hz chuyên game mượt mà",
      "Tấm nền IPS góc nhìn rộng 178 độ chuẩn màu"
    ],
    "imageUrl": "/images/monitor/asus-tuf-gaming-vg27aq-80c7806acde7.jpg",
    "images": [
      "/images/monitor/asus-tuf-gaming-vg27aq-80c7806acde7.jpg"
    ],
    "price": 6480000,
    "originalPrice": 7260000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-80c7806a-1",
        "productId": "80c7806acde7949635c084a5fa6fcdf20a0dd8816d86fa7c56f59a5e4be6738f",
        "sku": "SKU-80C7806A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 6480000,
        "originalPrice": 7260000,
        "costPrice": 5314000,
        "status": "active"
      }
    ],
    "specs": {
      "screen_inch": 27,
      "panel": "IPS",
      "refresh_hz": 165,
      "resolution": "2560 x 1440 (2K)"
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "70dc0d3fe32cc2116bdc20e7abac3a3521fa7a29469eb12c70cf87603895d569",
    "categoryId": "cat-monitor",
    "categorySlug": "monitor",
    "brandId": "b-ch-nh-h-ng",
    "brandName": "Chính hãng",
    "name": "LG UltraGear 27GR75Q-B",
    "slug": "lg-ultragear-27gr75q-b",
    "description": "LG UltraGear 27GR75Q-B chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Kích thước 27 inch độ phân giải 2560 x 1440 (2K)",
      "Tần số quét cao 165Hz chuyên game mượt mà",
      "Tấm nền IPS góc nhìn rộng 178 độ chuẩn màu"
    ],
    "imageUrl": "/images/monitor/aoc-24g4xe-a0778acc1ac5.png",
    "images": [
      "/images/monitor/aoc-24g4xe-a0778acc1ac5.png"
    ],
    "price": 6710000,
    "originalPrice": 7520000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-70dc0d3f-1",
        "productId": "70dc0d3fe32cc2116bdc20e7abac3a3521fa7a29469eb12c70cf87603895d569",
        "sku": "SKU-70DC0D3F",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 6710000,
        "originalPrice": 7520000,
        "costPrice": 5502000,
        "status": "active"
      }
    ],
    "specs": {
      "screen_inch": 27,
      "panel": "IPS",
      "refresh_hz": 165,
      "resolution": "2560 x 1440 (2K)"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "04f6563432c9e6d59a08bfa9512cfdcab626ad27a373036db796960f048fa395",
    "categoryId": "cat-monitor",
    "categorySlug": "monitor",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI G255F",
    "slug": "msi-g255f",
    "description": "MSI G255F chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Kích thước 24 inch độ phân giải 1920 x 1080 (FHD)",
      "Tần số quét cao 165Hz chuyên game mượt mà",
      "Tấm nền IPS góc nhìn rộng 178 độ chuẩn màu"
    ],
    "imageUrl": "/images/monitor/aoc-24g4xe-a0778acc1ac5.png",
    "images": [
      "/images/monitor/aoc-24g4xe-a0778acc1ac5.png"
    ],
    "price": 3190000,
    "originalPrice": 3570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-04f65634-1",
        "productId": "04f6563432c9e6d59a08bfa9512cfdcab626ad27a373036db796960f048fa395",
        "sku": "SKU-04F65634",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3190000,
        "originalPrice": 3570000,
        "costPrice": 2616000,
        "status": "active"
      }
    ],
    "specs": {
      "screen_inch": 24,
      "panel": "IPS",
      "refresh_hz": 165,
      "resolution": "1920 x 1080 (FHD)"
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 2
    }
  },
  {
    "id": "3335cb6d8ee5ff7444645ea3146c243526098ee5d1a9bf95e406f666661a8a1d",
    "categoryId": "cat-psu",
    "categorySlug": "psu",
    "brandId": "b-corsair",
    "brandName": "Corsair",
    "name": "Corsair RM750e (2025)",
    "slug": "corsair-rm750e-2025",
    "description": "Corsair RM750e (2025) chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Công suất thực 750W đạt chuẩn 80 Plus Gold",
      "Thiết kế full modular dây cáp gọn gàng",
      "Linh kiện tụ điện Nhật Bản bền bỉ, an toàn điện áp"
    ],
    "imageUrl": "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg",
    "images": [
      "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg"
    ],
    "price": 2800000,
    "originalPrice": 3140000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-3335cb6d-1",
        "productId": "3335cb6d8ee5ff7444645ea3146c243526098ee5d1a9bf95e406f666661a8a1d",
        "sku": "SKU-3335CB6D",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2800000,
        "originalPrice": 3140000,
        "costPrice": 2156000,
        "status": "active"
      }
    ],
    "specs": {
      "psu_watt": 750,
      "modular": "full",
      "certification": "80 Plus Gold"
    },
    "stockStatus": {
      "status": "low_stock",
      "availableQty": 3
    }
  },
  {
    "id": "ee59b9f517117dd598b100a03bd4952cee24905dfdc5557a985baa46ff624bf2",
    "categoryId": "cat-psu",
    "categorySlug": "psu",
    "brandId": "b-corsair",
    "brandName": "Corsair",
    "name": "Corsair RM850e (2025)",
    "slug": "corsair-rm850e-2025",
    "description": "Corsair RM850e (2025) chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Công suất thực 650W đạt chuẩn 80 Plus Gold",
      "Thiết kế full modular dây cáp gọn gàng",
      "Linh kiện tụ điện Nhật Bản bền bỉ, an toàn điện áp"
    ],
    "imageUrl": "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg",
    "images": [
      "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg"
    ],
    "price": 3010000,
    "originalPrice": 3370000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-ee59b9f5-1",
        "productId": "ee59b9f517117dd598b100a03bd4952cee24905dfdc5557a985baa46ff624bf2",
        "sku": "SKU-EE59B9F5",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3010000,
        "originalPrice": 3370000,
        "costPrice": 2318000,
        "status": "active"
      }
    ],
    "specs": {
      "psu_watt": 650,
      "modular": "full",
      "certification": "80 Plus Gold"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "3df5e885dd92eb0757698f9765403d14d45f51b9266d10dd725511772d7f4ebe",
    "categoryId": "cat-psu",
    "categorySlug": "psu",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI MAG A650BN",
    "slug": "msi-mag-a650bn",
    "description": "MSI MAG A650BN chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Công suất thực 650W đạt chuẩn 80 Plus Bronze",
      "Thiết kế non modular dây cáp gọn gàng",
      "Linh kiện tụ điện Nhật Bản bền bỉ, an toàn điện áp"
    ],
    "imageUrl": "/images/power-supply/msi-mag-a650bn-3df5e885dd92.jpg",
    "images": [
      "/images/power-supply/msi-mag-a650bn-3df5e885dd92.jpg"
    ],
    "price": 1950000,
    "originalPrice": 2180000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-3df5e885-1",
        "productId": "3df5e885dd92eb0757698f9765403d14d45f51b9266d10dd725511772d7f4ebe",
        "sku": "SKU-3DF5E885",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1950000,
        "originalPrice": 2180000,
        "costPrice": 1502000,
        "status": "active"
      }
    ],
    "specs": {
      "psu_watt": 650,
      "modular": "non",
      "certification": "80 Plus Bronze"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "1e1acb4461bc7bf000a8d2210b3ad79b4861a7c641259e46d479103fe7216efa",
    "categoryId": "cat-psu",
    "categorySlug": "psu",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI MAG A750GL PCIE5",
    "slug": "msi-mag-a750gl-pcie5",
    "description": "MSI MAG A750GL PCIE5 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Công suất thực 750W đạt chuẩn 80 Plus Bronze",
      "Thiết kế non modular dây cáp gọn gàng",
      "Linh kiện tụ điện Nhật Bản bền bỉ, an toàn điện áp"
    ],
    "imageUrl": "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg",
    "images": [
      "/images/power-supply/corsair-rm750e-2025-3335cb6d8ee5.jpg"
    ],
    "price": 2840000,
    "originalPrice": 3180000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-1e1acb44-1",
        "productId": "1e1acb4461bc7bf000a8d2210b3ad79b4861a7c641259e46d479103fe7216efa",
        "sku": "SKU-1E1ACB44",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2840000,
        "originalPrice": 3180000,
        "costPrice": 2187000,
        "status": "active"
      }
    ],
    "specs": {
      "psu_watt": 750,
      "modular": "non",
      "certification": "80 Plus Bronze"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "517c4a98422aebc21becdfdb794bfe83b9eff9b2d5e7c8ad960366426829742a",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-corsair",
    "brandName": "Corsair",
    "name": "Corsair Vengeance LPX 16 GB",
    "slug": "corsair-vengeance-lpx-16-gb",
    "description": "Corsair Vengeance LPX 16 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR5 Bus 6000MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg",
    "images": [
      "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg"
    ],
    "price": 1170000,
    "originalPrice": 1310000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-517c4a98-1",
        "productId": "517c4a98422aebc21becdfdb794bfe83b9eff9b2d5e7c8ad960366426829742a",
        "sku": "SKU-517C4A98",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1170000,
        "originalPrice": 1310000,
        "costPrice": 901000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR5",
      "ram_gb": 32,
      "ram_speed_mhz": 6000
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "3d8f348c2fc4efa25e9ee48c76bb796666ad8f793845a6e6a8483fd96900eb93",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-corsair",
    "brandName": "Corsair",
    "name": "Corsair Vengeance RGB 32 GB",
    "slug": "corsair-vengeance-rgb-32-gb",
    "description": "Corsair Vengeance RGB 32 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR5 Bus 6000MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg",
    "images": [
      "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg"
    ],
    "price": 2400000,
    "originalPrice": 2690000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-3d8f348c-1",
        "productId": "3d8f348c2fc4efa25e9ee48c76bb796666ad8f793845a6e6a8483fd96900eb93",
        "sku": "SKU-3D8F348C",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2400000,
        "originalPrice": 2690000,
        "costPrice": 1848000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR5",
      "ram_gb": 32,
      "ram_speed_mhz": 6000
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "c63a970ec7f23608647b6d793a91cb366a2f0bde79c61824be1bff84b5f280cf",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-g-skill",
    "brandName": "G.Skill",
    "name": "G.Skill Ripjaws V 32 GB",
    "slug": "g-skill-ripjaws-v-32-gb",
    "description": "G.Skill Ripjaws V 32 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR4 Bus 3200MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/g-skill-ripjaws-v-32-gb-c63a970ec7f2.jpg",
    "images": [
      "/images/memory/g-skill-ripjaws-v-32-gb-c63a970ec7f2.jpg"
    ],
    "price": 2010000,
    "originalPrice": 2250000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-c63a970e-1",
        "productId": "c63a970ec7f23608647b6d793a91cb366a2f0bde79c61824be1bff84b5f280cf",
        "sku": "SKU-C63A970E",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2010000,
        "originalPrice": 2250000,
        "costPrice": 1548000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR4",
      "ram_gb": 32,
      "ram_speed_mhz": 3200
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "92d139676d3d197432453358850c32977d1fd7a76a2a5f83c684f62ecb16e359",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-g-skill",
    "brandName": "G.Skill",
    "name": "G.Skill Trident Z5 RGB 64 GB",
    "slug": "g-skill-trident-z5-rgb-64-gb",
    "description": "G.Skill Trident Z5 RGB 64 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR5 Bus 6000MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg",
    "images": [
      "/images/memory/corsair-vengeance-rgb-32-gb-3d8f348c2fc4.jpg"
    ],
    "price": 5880000,
    "originalPrice": 6590000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-92d13967-1",
        "productId": "92d139676d3d197432453358850c32977d1fd7a76a2a5f83c684f62ecb16e359",
        "sku": "SKU-92D13967",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 5880000,
        "originalPrice": 6590000,
        "costPrice": 4528000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR5",
      "ram_gb": 32,
      "ram_speed_mhz": 6000
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 4
    }
  },
  {
    "id": "f93e886025717109d535f8b601c627694977190384d0a14e5f50ddb22867d94e",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-kingston",
    "brandName": "Kingston",
    "name": "Kingston FURY Beast 32 GB",
    "slug": "kingston-fury-beast-32-gb",
    "description": "Kingston FURY Beast 32 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR5 Bus 6000MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/kingston-fury-beast-32-gb-f93e88602571.webp",
    "images": [
      "/images/memory/kingston-fury-beast-32-gb-f93e88602571.webp"
    ],
    "price": 3430000,
    "originalPrice": 3840000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-f93e8860-1",
        "productId": "f93e886025717109d535f8b601c627694977190384d0a14e5f50ddb22867d94e",
        "sku": "SKU-F93E8860",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3430000,
        "originalPrice": 3840000,
        "costPrice": 2641000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR5",
      "ram_gb": 32,
      "ram_speed_mhz": 6000
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "0cce20938aae4a0802e0d840347b6878e13884e9ea5da7b72577c6ca59fd0e86",
    "categoryId": "cat-ram",
    "categorySlug": "ram",
    "brandId": "b-teamgroup",
    "brandName": "TEAMGROUP",
    "name": "TEAMGROUP T-Force Delta RGB 32 GB",
    "slug": "teamgroup-t-force-delta-rgb-32-gb",
    "description": "TEAMGROUP T-Force Delta RGB 32 GB chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 32GB chuẩn DDR5 Bus 6000MHz",
      "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
      "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
    ],
    "imageUrl": "/images/memory/teamgroup-t-force-delta-rgb-32-gb-0cce20938aae.jpg",
    "images": [
      "/images/memory/teamgroup-t-force-delta-rgb-32-gb-0cce20938aae.jpg"
    ],
    "price": 2670000,
    "originalPrice": 2990000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-0cce2093-1",
        "productId": "0cce20938aae4a0802e0d840347b6878e13884e9ea5da7b72577c6ca59fd0e86",
        "sku": "SKU-0CCE2093",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2670000,
        "originalPrice": 2990000,
        "costPrice": 2056000,
        "status": "active"
      }
    ],
    "specs": {
      "ram_type": "DDR5",
      "ram_gb": 32,
      "ram_speed_mhz": 6000
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "64dc7f047585e37bf0becd21f1d5d8ec58a9b06dbcb991bb0ef34edbf525163c",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-crucial",
    "brandName": "Crucial",
    "name": "Crucial P3 Plus",
    "slug": "crucial-p3-plus",
    "description": "Crucial P3 Plus chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/crucial-p3-plus-64dc7f047585.jpg",
    "images": [
      "/images/internal-hard-drive/crucial-p3-plus-64dc7f047585.jpg"
    ],
    "price": 1520000,
    "originalPrice": 1700000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-64dc7f04-1",
        "productId": "64dc7f047585e37bf0becd21f1d5d8ec58a9b06dbcb991bb0ef34edbf525163c",
        "sku": "SKU-64DC7F04",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1520000,
        "originalPrice": 1700000,
        "costPrice": 1216000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "e4d1eb6b8e55c3b81ecf7c6fac1e76374fff51516138b575a77e9963318bd4aa",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-crucial",
    "brandName": "Crucial",
    "name": "Crucial P510",
    "slug": "crucial-p510",
    "description": "Crucial P510 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png",
    "images": [
      "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png"
    ],
    "price": 2650000,
    "originalPrice": 2970000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-e4d1eb6b-1",
        "productId": "e4d1eb6b8e55c3b81ecf7c6fac1e76374fff51516138b575a77e9963318bd4aa",
        "sku": "SKU-E4D1EB6B",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 2650000,
        "originalPrice": 2970000,
        "costPrice": 2120000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "15311338f518072cfa659390b765f41584c33a22b249885c4d1591dc9aa7af81",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-kingston",
    "brandName": "Kingston",
    "name": "Kingston KC3000",
    "slug": "kingston-kc3000",
    "description": "Kingston KC3000 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png",
    "images": [
      "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png"
    ],
    "price": 4420000,
    "originalPrice": 4950000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-15311338-1",
        "productId": "15311338f518072cfa659390b765f41584c33a22b249885c4d1591dc9aa7af81",
        "sku": "SKU-15311338",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 4420000,
        "originalPrice": 4950000,
        "costPrice": 3536000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "cdc875d18109ca5c457ea2feee66cd5cb9f055700d6d0c0cffeacb398a8ea0bd",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-kingston",
    "brandName": "Kingston",
    "name": "Kingston NV2",
    "slug": "kingston-nv2",
    "description": "Kingston NV2 chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/kingston-nv2-cdc875d18109.jpg",
    "images": [
      "/images/internal-hard-drive/kingston-nv2-cdc875d18109.jpg"
    ],
    "price": 1830000,
    "originalPrice": 2050000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-cdc875d1-1",
        "productId": "cdc875d18109ca5c457ea2feee66cd5cb9f055700d6d0c0cffeacb398a8ea0bd",
        "sku": "SKU-CDC875D1",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 1830000,
        "originalPrice": 2050000,
        "costPrice": 1464000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "285147ac7837de424abf63c75ada6f00bc439a271a550ee23866b385b330fcd0",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-samsung",
    "brandName": "Samsung",
    "name": "Samsung 970 Evo Plus",
    "slug": "samsung-970-evo-plus",
    "description": "Samsung 970 Evo Plus chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png",
    "images": [
      "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png"
    ],
    "price": 3560000,
    "originalPrice": 3990000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-285147ac-1",
        "productId": "285147ac7837de424abf63c75ada6f00bc439a271a550ee23866b385b330fcd0",
        "sku": "SKU-285147AC",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3560000,
        "originalPrice": 3990000,
        "costPrice": 2848000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "7dc2b0b34bb68c72e9cf9eef4e232e51642bca2aba11dc870d6fed57c34c962b",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-samsung",
    "brandName": "Samsung",
    "name": "Samsung 980 Pro",
    "slug": "samsung-980-pro",
    "description": "Samsung 980 Pro chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 1000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png",
    "images": [
      "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png"
    ],
    "price": 5150000,
    "originalPrice": 5770000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-7dc2b0b3-1",
        "productId": "7dc2b0b34bb68c72e9cf9eef4e232e51642bca2aba11dc870d6fed57c34c962b",
        "sku": "SKU-7DC2B0B3",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 5150000,
        "originalPrice": 5770000,
        "costPrice": 4120000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 1000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 6
    }
  },
  {
    "id": "b182cda76ba681d381cb42f7cd4a01b11f7b0aa88fdec3667cd7b6ab66b69a58",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-samsung",
    "brandName": "Samsung",
    "name": "Samsung 990 Pro",
    "slug": "samsung-990-pro",
    "description": "Samsung 990 Pro chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 2000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png",
    "images": [
      "/images/internal-hard-drive/samsung-990-pro-b182cda76ba6.png"
    ],
    "price": 3960000,
    "originalPrice": 4440000,
    "discountPercent": 11,
    "isHot": true,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-b182cda7-1",
        "productId": "b182cda76ba681d381cb42f7cd4a01b11f7b0aa88fdec3667cd7b6ab66b69a58",
        "sku": "SKU-B182CDA7",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3960000,
        "originalPrice": 4440000,
        "costPrice": 3168000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 2000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "9db57a7d1b0bc53af235b27053f8656666b2d00f1383fa0f1ff664debf32b860",
    "categoryId": "cat-ssd",
    "categorySlug": "ssd",
    "brandId": "b-western-digital",
    "brandName": "Western Digital",
    "name": "Western Digital WD_Black SN850X",
    "slug": "western-digital-wd-black-sn850x",
    "description": "Western Digital WD_Black SN850X chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "Dung lượng 2000GB chuẩn NVMe M.2 PCIe Gen 4x4",
      "Tốc độ đọc ghi cực nhanh",
      "Bảo hành chính hãng 5 năm an tâm dữ liệu"
    ],
    "imageUrl": "/images/internal-hard-drive/western-digital-wd-black-sn850x-9db57a7d1b0b.jpg",
    "images": [
      "/images/internal-hard-drive/western-digital-wd-black-sn850x-9db57a7d1b0b.jpg"
    ],
    "price": 3860000,
    "originalPrice": 4320000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-9db57a7d-1",
        "productId": "9db57a7d1b0bc53af235b27053f8656666b2d00f1383fa0f1ff664debf32b860",
        "sku": "SKU-9DB57A7D",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 3860000,
        "originalPrice": 4320000,
        "costPrice": 3088000,
        "status": "active"
      }
    ],
    "specs": {
      "storage_gb": 2000,
      "storage_type": "NVMe",
      "interface": "NVMe M.2"
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "752d9ae6e8f14d830d0e400d1b154957fb249003791d7d1709f586b5b7a199e1",
    "categoryId": "cat-vga",
    "categorySlug": "vga",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI GeForce RTX 3060 Ventus 2X 12G",
    "slug": "msi-geforce-rtx-3060-ventus-2x-12g",
    "description": "MSI GeForce RTX 3060 Ventus 2X 12G chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "VRAM 8GB GDDR6 hiệu năng đỉnh cao",
      "Chiều dài VGA 307mm phù hợp đa số case",
      "Hỗ trợ Ray Tracing thế hệ mới và DLSS 3.5 siêu mượt"
    ],
    "imageUrl": "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg",
    "images": [
      "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg"
    ],
    "price": 7810000,
    "originalPrice": 8750000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-752d9ae6-1",
        "productId": "752d9ae6e8f14d830d0e400d1b154957fb249003791d7d1709f586b5b7a199e1",
        "sku": "SKU-752D9AE6",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 7810000,
        "originalPrice": 8750000,
        "costPrice": 6951000,
        "status": "active"
      }
    ],
    "specs": {
      "vram_gb": 8,
      "length_mm": 307,
      "tgp_w": 220
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  },
  {
    "id": "dca21cffcb61642e2da871ecfe078cd88013985349e2f9e3f27faac21a60e910",
    "categoryId": "cat-vga",
    "categorySlug": "vga",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI RTX 4060 Ti 8G GAMING SLIM MONSTER HUNTER EDITION",
    "slug": "msi-rtx-4060-ti-8g-gaming-slim-monster-hunter-edition",
    "description": "MSI RTX 4060 Ti 8G GAMING SLIM MONSTER HUNTER EDITION chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "VRAM 8GB GDDR6 hiệu năng đỉnh cao",
      "Chiều dài VGA 307mm phù hợp đa số case",
      "Hỗ trợ Ray Tracing thế hệ mới và DLSS 3.5 siêu mượt"
    ],
    "imageUrl": "/images/video-card/msi-rtx-4060-ti-8g-gaming-slim-monster-hunter-edition-dca21cffcb61.webp",
    "images": [
      "/images/video-card/msi-rtx-4060-ti-8g-gaming-slim-monster-hunter-edition-dca21cffcb61.webp"
    ],
    "price": 14680000,
    "originalPrice": 16440000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-dca21cff-1",
        "productId": "dca21cffcb61642e2da871ecfe078cd88013985349e2f9e3f27faac21a60e910",
        "sku": "SKU-DCA21CFF",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14680000,
        "originalPrice": 16440000,
        "costPrice": 13065000,
        "status": "active"
      }
    ],
    "specs": {
      "vram_gb": 8,
      "length_mm": 307,
      "tgp_w": 160
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 5
    }
  },
  {
    "id": "fc17a74f18090fc0987486a04ce4529961a6ff56408b2576b9674d5ed8599864",
    "categoryId": "cat-vga",
    "categorySlug": "vga",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI RTX 4070 Ti SUPER 16G VENTUS 3X BLACK OC",
    "slug": "msi-rtx-4070-ti-super-16g-ventus-3x-black-oc",
    "description": "MSI RTX 4070 Ti SUPER 16G VENTUS 3X BLACK OC chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "VRAM 16GB GDDR6 hiệu năng đỉnh cao",
      "Chiều dài VGA 307mm phù hợp đa số case",
      "Hỗ trợ Ray Tracing thế hệ mới và DLSS 3.5 siêu mượt"
    ],
    "imageUrl": "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg",
    "images": [
      "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg"
    ],
    "price": 14490000,
    "originalPrice": 16230000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": false,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-fc17a74f-1",
        "productId": "fc17a74f18090fc0987486a04ce4529961a6ff56408b2576b9674d5ed8599864",
        "sku": "SKU-FC17A74F",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 14490000,
        "originalPrice": 16230000,
        "costPrice": 12896000,
        "status": "active"
      }
    ],
    "specs": {
      "vram_gb": 16,
      "length_mm": 307,
      "tgp_w": 220
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 8
    }
  },
  {
    "id": "3a40ad6ac20ca8e772a09d6f23a7eb4f24755e6c8a31f3754bb5eb897d277e2a",
    "categoryId": "cat-vga",
    "categorySlug": "vga",
    "brandId": "b-msi",
    "brandName": "MSI",
    "name": "MSI RTX 5060 Ti 16G INSPIRE 2X OC",
    "slug": "msi-rtx-5060-ti-16g-inspire-2x-oc",
    "description": "MSI RTX 5060 Ti 16G INSPIRE 2X OC chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
    "highlights": [
      "VRAM 16GB GDDR6 hiệu năng đỉnh cao",
      "Chiều dài VGA 204mm phù hợp đa số case",
      "Hỗ trợ Ray Tracing thế hệ mới và DLSS 3.5 siêu mượt"
    ],
    "imageUrl": "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg",
    "images": [
      "/images/video-card/msi-rtx-5060-ti-16g-inspire-2x-oc-3a40ad6ac20c.jpg"
    ],
    "price": 13010000,
    "originalPrice": 14570000,
    "discountPercent": 11,
    "isHot": false,
    "isNew": true,
    "hasInstallment0": true,
    "status": "active",
    "createdAt": "2026-10-19T08:00:00Z",
    "variants": [
      {
        "id": "var-3a40ad6a-1",
        "productId": "3a40ad6ac20ca8e772a09d6f23a7eb4f24755e6c8a31f3754bb5eb897d277e2a",
        "sku": "SKU-3A40AD6A",
        "name": "Bản tiêu chuẩn chính hãng",
        "price": 13010000,
        "originalPrice": 14570000,
        "costPrice": 11579000,
        "status": "active"
      }
    ],
    "specs": {
      "vram_gb": 16,
      "length_mm": 204,
      "tgp_w": 220
    },
    "stockStatus": {
      "status": "in_stock",
      "availableQty": 7
    }
  }
];

export const INITIAL_PROMOTIONS: Promotion[] = [
  {
    id: 'promo-01',
    name: 'Flash Sale Cuối Tuần - Bùng Nổ Công Nghệ',
    type: 'percentage',
    value: 12,
    description: 'Giảm sốc đến 12% trực tiếp trên giá bán cho tất cả Laptop OLED và Gaming chọn lọc.',
    startsAt: '2026-10-16T00:00:00Z',
    endsAt: '2026-10-18T23:59:59Z',
    isFlashSale: true,
    flashSaleTotalQuota: 50,
    flashSaleRemainingQuota: 18,
    applicableCategorySlugs: ['laptop']
  },
  {
    id: 'promo-02',
    name: 'Trả Góp 0% Lãi Suất - Kỳ Hạn Đến 12 Tháng',
    type: 'zero_installment',
    value: 0,
    description: 'Áp dụng cho mọi đơn hàng Laptop và Bộ máy PC trên 15 triệu đồng qua thẻ tín dụng hoặc công ty tài chính.',
    startsAt: '2026-10-01T00:00:00Z',
    endsAt: '2026-12-31T23:59:59Z'
  },
  {
    id: 'promo-03',
    name: 'Tặng Chuột Không Dây & Balo TechStore Cao Cấp',
    type: 'gift',
    value: 500000,
    description: 'Tặng combo Balo chống nước TechStore + Chuột không dây trị giá 500.000₫ khi mua laptop văn phòng bất kỳ.',
    startsAt: '2026-10-01T00:00:00Z',
    endsAt: '2026-10-31T23:59:59Z',
    applicableCategorySlugs: ['laptop']
  }
];


export const INITIAL_STRATEGIC_DOCUMENTS: StrategicDocument[] = [
  {
    "id": "sales-plan-2025-Q4",
    "docType": "sales_plan",
    "title": "Kế hoạch bán hàng 2025-Q4",
    "period": "2025-Q4",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Kế hoạch bán hàng 2025-Q4\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Mục tiêu doanh thu\n\nKỳ: 2025-Q4. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 4671000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2025-10 | 1323000000 |\n| 2025-11 | 1755000000 |\n| 2025-12 | 1593000000 |\n\n## Theo dõi và giới hạn\n\nĐối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.\n\n## Ngân sách\n\nMarketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2025-Q4-1",
        "headingPath": "Kế hoạch bán hàng 2025-Q4 > Kế hoạch bán hàng 2025-Q4",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "kinh",
          "retail_sim_v1",
          "hay",
          "2025",
          "shop"
        ]
      },
      {
        "id": "chunk-sales-plan-2025-Q4-2",
        "headingPath": "Kế hoạch bán hàng 2025-Q4 > Mục tiêu doanh thu",
        "text": "Kỳ: 2025-Q4. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 4671000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2025-10 | 1323000000 |\n| 2025-11 | 1755000000 |\n| 2025-12 | 1593000000 |",
        "keywords": [
          "doanh",
          "vnd",
          "theo",
          "4671000000",
          "1755000000",
          "vat",
          "1323000000",
          "thu"
        ]
      },
      {
        "id": "chunk-sales-plan-2025-Q4-3",
        "headingPath": "Kế hoạch bán hàng 2025-Q4 > Theo dõi và giới hạn",
        "text": "Đối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.",
        "keywords": [
          "theo",
          "doanh",
          "fifo",
          "suy",
          "quan",
          "financial_ledger",
          "thu"
        ]
      },
      {
        "id": "chunk-sales-plan-2025-Q4-4",
        "headingPath": "Kế hoạch bán hàng 2025-Q4 > Ngân sách",
        "text": "Marketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
        "keywords": [
          "vnd",
          "marketing",
          "thay",
          "12000000",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2025-Q4-draft",
    "docType": "sales_plan",
    "title": "BẢN NHÁP kế hoạch 2025-Q4",
    "period": "2025-Q4",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# BẢN NHÁP kế hoạch 2025-Q4\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4871000000 VND. Không dùng làm mục tiêu chính thức.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2025-Q4-draft-1",
        "headingPath": "BẢN NHÁP kế hoạch 2025-Q4 > BẢN NHÁP kế hoạch 2025-Q4",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4871000000 VND. Không dùng làm mục tiêu chính thức.",
        "keywords": [
          "doanh",
          "vnd",
          "4871000000",
          "kinh",
          "retail_sim_v1",
          "hay",
          "2025",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q1",
    "docType": "sales_plan",
    "title": "Kế hoạch bán hàng 2026-Q1",
    "period": "2026-Q1",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Kế hoạch bán hàng 2026-Q1\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Mục tiêu doanh thu\n\nKỳ: 2026-Q1. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 3658000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-01 | 1512000000 |\n| 2026-02 | 918000000 |\n| 2026-03 | 1228000000 |\n\n## Theo dõi và giới hạn\n\nĐối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.\n\n## Ngân sách\n\nMarketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q1-1",
        "headingPath": "Kế hoạch bán hàng 2026-Q1 > Kế hoạch bán hàng 2026-Q1",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q1-2",
        "headingPath": "Kế hoạch bán hàng 2026-Q1 > Mục tiêu doanh thu",
        "text": "Kỳ: 2026-Q1. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 3658000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-01 | 1512000000 |\n| 2026-02 | 918000000 |\n| 2026-03 | 1228000000 |",
        "keywords": [
          "doanh",
          "3658000000",
          "vnd",
          "theo",
          "1228000000",
          "2026",
          "vat",
          "1512000000"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q1-3",
        "headingPath": "Kế hoạch bán hàng 2026-Q1 > Theo dõi và giới hạn",
        "text": "Đối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.",
        "keywords": [
          "theo",
          "doanh",
          "fifo",
          "suy",
          "quan",
          "financial_ledger",
          "thu"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q1-4",
        "headingPath": "Kế hoạch bán hàng 2026-Q1 > Ngân sách",
        "text": "Marketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
        "keywords": [
          "vnd",
          "marketing",
          "thay",
          "12000000",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q1-draft",
    "docType": "sales_plan",
    "title": "BẢN NHÁP kế hoạch 2026-Q1",
    "period": "2026-Q1",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# BẢN NHÁP kế hoạch 2026-Q1\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 3858000000 VND. Không dùng làm mục tiêu chính thức.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q1-draft-1",
        "headingPath": "BẢN NHÁP kế hoạch 2026-Q1 > BẢN NHÁP kế hoạch 2026-Q1",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 3858000000 VND. Không dùng làm mục tiêu chính thức.",
        "keywords": [
          "doanh",
          "vnd",
          "2026",
          "3858000000",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q2",
    "docType": "sales_plan",
    "title": "Kế hoạch bán hàng 2026-Q2",
    "period": "2026-Q2",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Kế hoạch bán hàng 2026-Q2\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Mục tiêu doanh thu\n\nKỳ: 2026-Q2. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 3848000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-04 | 1269000000 |\n| 2026-05 | 1310000000 |\n| 2026-06 | 1269000000 |\n\n## Theo dõi và giới hạn\n\nĐối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.\n\n## Ngân sách\n\nMarketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q2-1",
        "headingPath": "Kế hoạch bán hàng 2026-Q2 > Kế hoạch bán hàng 2026-Q2",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q2-2",
        "headingPath": "Kế hoạch bán hàng 2026-Q2 > Mục tiêu doanh thu",
        "text": "Kỳ: 2026-Q2. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 3848000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-04 | 1269000000 |\n| 2026-05 | 1310000000 |\n| 2026-06 | 1269000000 |",
        "keywords": [
          "doanh",
          "vnd",
          "theo",
          "1310000000",
          "2026",
          "3848000000",
          "1269000000",
          "vat"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q2-3",
        "headingPath": "Kế hoạch bán hàng 2026-Q2 > Theo dõi và giới hạn",
        "text": "Đối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.",
        "keywords": [
          "theo",
          "doanh",
          "fifo",
          "suy",
          "quan",
          "financial_ledger",
          "thu"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q2-4",
        "headingPath": "Kế hoạch bán hàng 2026-Q2 > Ngân sách",
        "text": "Marketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
        "keywords": [
          "vnd",
          "marketing",
          "thay",
          "12000000",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q2-draft",
    "docType": "sales_plan",
    "title": "BẢN NHÁP kế hoạch 2026-Q2",
    "period": "2026-Q2",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# BẢN NHÁP kế hoạch 2026-Q2\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4048000000 VND. Không dùng làm mục tiêu chính thức.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q2-draft-1",
        "headingPath": "BẢN NHÁP kế hoạch 2026-Q2 > BẢN NHÁP kế hoạch 2026-Q2",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4048000000 VND. Không dùng làm mục tiêu chính thức.",
        "keywords": [
          "doanh",
          "vnd",
          "2026",
          "kinh",
          "4048000000",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q3",
    "docType": "sales_plan",
    "title": "Kế hoạch bán hàng 2026-Q3",
    "period": "2026-Q3",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Kế hoạch bán hàng 2026-Q3\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Mục tiêu doanh thu\n\nKỳ: 2026-Q3. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 4698000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-07 | 1377000000 |\n| 2026-08 | 1782000000 |\n| 2026-09 | 1539000000 |\n\n## Theo dõi và giới hạn\n\nĐối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.\n\n## Ngân sách\n\nMarketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q3-1",
        "headingPath": "Kế hoạch bán hàng 2026-Q3 > Kế hoạch bán hàng 2026-Q3",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q3-2",
        "headingPath": "Kế hoạch bán hàng 2026-Q3 > Mục tiêu doanh thu",
        "text": "Kỳ: 2026-Q3. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 4698000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n| 2026-07 | 1377000000 |\n| 2026-08 | 1782000000 |\n| 2026-09 | 1539000000 |",
        "keywords": [
          "doanh",
          "vnd",
          "theo",
          "1377000000",
          "2026",
          "vat",
          "4698000000",
          "1782000000"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q3-3",
        "headingPath": "Kế hoạch bán hàng 2026-Q3 > Theo dõi và giới hạn",
        "text": "Đối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.",
        "keywords": [
          "theo",
          "doanh",
          "fifo",
          "suy",
          "quan",
          "financial_ledger",
          "thu"
        ]
      },
      {
        "id": "chunk-sales-plan-2026-Q3-4",
        "headingPath": "Kế hoạch bán hàng 2026-Q3 > Ngân sách",
        "text": "Marketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.",
        "keywords": [
          "vnd",
          "marketing",
          "thay",
          "12000000",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "sales-plan-2026-Q3-draft",
    "docType": "sales_plan",
    "title": "BẢN NHÁP kế hoạch 2026-Q3",
    "period": "2026-Q3",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# BẢN NHÁP kế hoạch 2026-Q3\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4898000000 VND. Không dùng làm mục tiêu chính thức.",
    "chunks": [
      {
        "id": "chunk-sales-plan-2026-Q3-draft-1",
        "headingPath": "BẢN NHÁP kế hoạch 2026-Q3 > BẢN NHÁP kế hoạch 2026-Q3",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\nChưa duyệt. Mục tiêu dự thảo 4898000000 VND. Không dùng làm mục tiêu chính thức.",
        "keywords": [
          "doanh",
          "vnd",
          "4898000000",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2025-10",
    "docType": "management_report",
    "title": "Báo cáo tháng 2025-10",
    "period": "2025-10",
    "effectiveFrom": "2025-11-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2025-10\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2025-10\n\nDoanh thu thuần: 984310000 VND. Giá vốn: 839604000 VND. Lợi nhuận gộp: 144706000 VND. Chi phí vận hành: 108627410 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 36078590 VND. Đơn hàng: 99. Sản phẩm hoàn trả: 1.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2025-10-1",
        "headingPath": "Báo cáo tháng 2025-10 > Báo cáo tháng 2025-10",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "kinh",
          "retail_sim_v1",
          "hay",
          "2025",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-10-2",
        "headingPath": "Báo cáo tháng 2025-10 > Kết quả kỳ 2025-10",
        "text": "Doanh thu thuần: 984310000 VND. Giá vốn: 839604000 VND. Lợi nhuận gộp: 144706000 VND. Chi phí vận hành: 108627410 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 36078590 VND. Đơn hàng: 99. Sản phẩm hoàn trả: 1.",
        "keywords": [
          "doanh",
          "vnd",
          "36078590",
          "144706000",
          "chi",
          "108627410",
          "vay",
          "thu"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-10-3",
        "headingPath": "Báo cáo tháng 2025-10 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2025-11",
    "docType": "management_report",
    "title": "Báo cáo tháng 2025-11",
    "period": "2025-11",
    "effectiveFrom": "2025-12-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2025-11\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2025-11\n\nDoanh thu thuần: 1493219000 VND. Giá vốn: 1294467000 VND. Lợi nhuận gộp: 198752000 VND. Chi phí vận hành: 138225409 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 60526591 VND. Đơn hàng: 151. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2025-11-1",
        "headingPath": "Báo cáo tháng 2025-11 > Báo cáo tháng 2025-11",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "kinh",
          "retail_sim_v1",
          "hay",
          "2025",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-11-2",
        "headingPath": "Báo cáo tháng 2025-11 > Kết quả kỳ 2025-11",
        "text": "Doanh thu thuần: 1493219000 VND. Giá vốn: 1294467000 VND. Lợi nhuận gộp: 198752000 VND. Chi phí vận hành: 138225409 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 60526591 VND. Đơn hàng: 151. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "1294467000",
          "chi",
          "198752000",
          "60526591",
          "vay",
          "151"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-11-3",
        "headingPath": "Báo cáo tháng 2025-11 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2025-12",
    "docType": "management_report",
    "title": "Báo cáo tháng 2025-12",
    "period": "2025-12",
    "effectiveFrom": "2026-01-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2025-12\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2025-12\n\nDoanh thu thuần: 1474785000 VND. Giá vốn: 1265608000 VND. Lợi nhuận gộp: 209177000 VND. Chi phí vận hành: 114022635 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 95154365 VND. Đơn hàng: 131. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2025-12-1",
        "headingPath": "Báo cáo tháng 2025-12 > Báo cáo tháng 2025-12",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "kinh",
          "retail_sim_v1",
          "hay",
          "2025",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-12-2",
        "headingPath": "Báo cáo tháng 2025-12 > Kết quả kỳ 2025-12",
        "text": "Doanh thu thuần: 1474785000 VND. Giá vốn: 1265608000 VND. Lợi nhuận gộp: 209177000 VND. Chi phí vận hành: 114022635 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 95154365 VND. Đơn hàng: 131. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "114022635",
          "chi",
          "1265608000",
          "vay",
          "209177000",
          "thu"
        ]
      },
      {
        "id": "chunk-monthly-report-2025-12-3",
        "headingPath": "Báo cáo tháng 2025-12 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-01",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-01",
    "period": "2026-01",
    "effectiveFrom": "2026-02-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-01\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-01\n\nDoanh thu thuần: 1077004000 VND. Giá vốn: 950747000 VND. Lợi nhuận gộp: 126257000 VND. Chi phí vận hành: 127647044 VND. Lợi nhuận hoạt động trước lãi vay và thuế: -1390044 VND. Đơn hàng: 126. Sản phẩm hoàn trả: 4.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-01-1",
        "headingPath": "Báo cáo tháng 2026-01 > Báo cáo tháng 2026-01",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-01-2",
        "headingPath": "Báo cáo tháng 2026-01 > Kết quả kỳ 2026-01",
        "text": "Doanh thu thuần: 1077004000 VND. Giá vốn: 950747000 VND. Lợi nhuận gộp: 126257000 VND. Chi phí vận hành: 127647044 VND. Lợi nhuận hoạt động trước lãi vay và thuế: -1390044 VND. Đơn hàng: 126. Sản phẩm hoàn trả: 4.",
        "keywords": [
          "doanh",
          "vnd",
          "126257000",
          "chi",
          "2026",
          "127647044",
          "1390044",
          "vay"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-01-3",
        "headingPath": "Báo cáo tháng 2026-01 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-02",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-02",
    "period": "2026-02",
    "effectiveFrom": "2026-03-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-02\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-02\n\nDoanh thu thuần: 609442000 VND. Giá vốn: 529597000 VND. Lợi nhuận gộp: 79845000 VND. Chi phí vận hành: 104503862 VND. Lợi nhuận hoạt động trước lãi vay và thuế: -24658862 VND. Đơn hàng: 65. Sản phẩm hoàn trả: 1.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-02-1",
        "headingPath": "Báo cáo tháng 2026-02 > Báo cáo tháng 2026-02",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-02-2",
        "headingPath": "Báo cáo tháng 2026-02 > Kết quả kỳ 2026-02",
        "text": "Doanh thu thuần: 609442000 VND. Giá vốn: 529597000 VND. Lợi nhuận gộp: 79845000 VND. Chi phí vận hành: 104503862 VND. Lợi nhuận hoạt động trước lãi vay và thuế: -24658862 VND. Đơn hàng: 65. Sản phẩm hoàn trả: 1.",
        "keywords": [
          "doanh",
          "vnd",
          "chi",
          "24658862",
          "2026",
          "609442000",
          "79845000",
          "vay"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-02-3",
        "headingPath": "Báo cáo tháng 2026-02 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-03",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-03",
    "period": "2026-03",
    "effectiveFrom": "2026-04-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-03\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-03\n\nDoanh thu thuần: 1203150000 VND. Giá vốn: 1024304000 VND. Lợi nhuận gộp: 178846000 VND. Chi phí vận hành: 111034650 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 67811350 VND. Đơn hàng: 135. Sản phẩm hoàn trả: 5.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-03-1",
        "headingPath": "Báo cáo tháng 2026-03 > Báo cáo tháng 2026-03",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-03-2",
        "headingPath": "Báo cáo tháng 2026-03 > Kết quả kỳ 2026-03",
        "text": "Doanh thu thuần: 1203150000 VND. Giá vốn: 1024304000 VND. Lợi nhuận gộp: 178846000 VND. Chi phí vận hành: 111034650 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 67811350 VND. Đơn hàng: 135. Sản phẩm hoàn trả: 5.",
        "keywords": [
          "doanh",
          "1203150000",
          "vnd",
          "178846000",
          "67811350",
          "chi",
          "2026",
          "135"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-03-3",
        "headingPath": "Báo cáo tháng 2026-03 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-04",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-04",
    "period": "2026-04",
    "effectiveFrom": "2026-05-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-04\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-04\n\nDoanh thu thuần: 997980000 VND. Giá vốn: 850948000 VND. Lợi nhuận gộp: 147032000 VND. Chi phí vận hành: 108777780 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 38254220 VND. Đơn hàng: 111. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-04-1",
        "headingPath": "Báo cáo tháng 2026-04 > Báo cáo tháng 2026-04",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-04-2",
        "headingPath": "Báo cáo tháng 2026-04 > Kết quả kỳ 2026-04",
        "text": "Doanh thu thuần: 997980000 VND. Giá vốn: 850948000 VND. Lợi nhuận gộp: 147032000 VND. Chi phí vận hành: 108777780 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 38254220 VND. Đơn hàng: 111. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "108777780",
          "997980000",
          "chi",
          "2026",
          "850948000",
          "147032000"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-04-3",
        "headingPath": "Báo cáo tháng 2026-04 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-05",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-05",
    "period": "2026-05",
    "effectiveFrom": "2026-06-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-05\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-05\n\nDoanh thu thuần: 1175440000 VND. Giá vốn: 1002931000 VND. Lợi nhuận gộp: 172509000 VND. Chi phí vận hành: 110729840 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 61779160 VND. Đơn hàng: 118. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-05-1",
        "headingPath": "Báo cáo tháng 2026-05 > Báo cáo tháng 2026-05",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-05-2",
        "headingPath": "Báo cáo tháng 2026-05 > Kết quả kỳ 2026-05",
        "text": "Doanh thu thuần: 1175440000 VND. Giá vốn: 1002931000 VND. Lợi nhuận gộp: 172509000 VND. Chi phí vận hành: 110729840 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 61779160 VND. Đơn hàng: 118. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "1175440000",
          "110729840",
          "chi",
          "2026",
          "1002931000",
          "vay"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-05-3",
        "headingPath": "Báo cáo tháng 2026-05 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-06",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-06",
    "period": "2026-06",
    "effectiveFrom": "2026-07-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-06\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-06\n\nDoanh thu thuần: 838580000 VND. Giá vốn: 717998000 VND. Lợi nhuận gộp: 120582000 VND. Chi phí vận hành: 107024380 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 13557620 VND. Đơn hàng: 96. Sản phẩm hoàn trả: 4.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-06-1",
        "headingPath": "Báo cáo tháng 2026-06 > Báo cáo tháng 2026-06",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-06-2",
        "headingPath": "Báo cáo tháng 2026-06 > Kết quả kỳ 2026-06",
        "text": "Doanh thu thuần: 838580000 VND. Giá vốn: 717998000 VND. Lợi nhuận gộp: 120582000 VND. Chi phí vận hành: 107024380 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 13557620 VND. Đơn hàng: 96. Sản phẩm hoàn trả: 4.",
        "keywords": [
          "doanh",
          "vnd",
          "838580000",
          "chi",
          "2026",
          "717998000",
          "13557620",
          "vay"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-06-3",
        "headingPath": "Báo cáo tháng 2026-06 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-07",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-07",
    "period": "2026-07",
    "effectiveFrom": "2026-08-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-07\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-07\n\nDoanh thu thuần: 1024280000 VND. Giá vốn: 888376000 VND. Lợi nhuận gộp: 135904000 VND. Chi phí vận hành: 109067080 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 26836920 VND. Đơn hàng: 101. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-07-1",
        "headingPath": "Báo cáo tháng 2026-07 > Báo cáo tháng 2026-07",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-07-2",
        "headingPath": "Báo cáo tháng 2026-07 > Kết quả kỳ 2026-07",
        "text": "Doanh thu thuần: 1024280000 VND. Giá vốn: 888376000 VND. Lợi nhuận gộp: 135904000 VND. Chi phí vận hành: 109067080 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 26836920 VND. Đơn hàng: 101. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "888376000",
          "109067080",
          "101",
          "1024280000",
          "chi",
          "2026"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-07-3",
        "headingPath": "Báo cáo tháng 2026-07 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-08",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-08",
    "period": "2026-08",
    "effectiveFrom": "2026-09-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-08\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-08\n\nDoanh thu thuần: 1427320000 VND. Giá vốn: 1240171000 VND. Lợi nhuận gộp: 187149000 VND. Chi phí vận hành: 141500520 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 45648480 VND. Đơn hàng: 163. Sản phẩm hoàn trả: 4.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-08-1",
        "headingPath": "Báo cáo tháng 2026-08 > Báo cáo tháng 2026-08",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-08-2",
        "headingPath": "Báo cáo tháng 2026-08 > Kết quả kỳ 2026-08",
        "text": "Doanh thu thuần: 1427320000 VND. Giá vốn: 1240171000 VND. Lợi nhuận gộp: 187149000 VND. Chi phí vận hành: 141500520 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 45648480 VND. Đơn hàng: 163. Sản phẩm hoàn trả: 4.",
        "keywords": [
          "doanh",
          "vnd",
          "141500520",
          "45648480",
          "chi",
          "1427320000",
          "2026",
          "187149000"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-08-3",
        "headingPath": "Báo cáo tháng 2026-08 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "monthly-report-2026-09",
    "docType": "management_report",
    "title": "Báo cáo tháng 2026-09",
    "period": "2026-09",
    "effectiveFrom": "2026-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Báo cáo tháng 2026-09\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Kết quả kỳ 2026-09\n\nDoanh thu thuần: 1189908000 VND. Giá vốn: 1010759000 VND. Lợi nhuận gộp: 179149000 VND. Chi phí vận hành: 110888988 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 68260012 VND. Đơn hàng: 131. Sản phẩm hoàn trả: 2.\n\n## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
    "chunks": [
      {
        "id": "chunk-monthly-report-2026-09-1",
        "headingPath": "Báo cáo tháng 2026-09 > Báo cáo tháng 2026-09",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "2026",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-09-2",
        "headingPath": "Báo cáo tháng 2026-09 > Kết quả kỳ 2026-09",
        "text": "Doanh thu thuần: 1189908000 VND. Giá vốn: 1010759000 VND. Lợi nhuận gộp: 179149000 VND. Chi phí vận hành: 110888988 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 68260012 VND. Đơn hàng: 131. Sản phẩm hoàn trả: 2.",
        "keywords": [
          "doanh",
          "vnd",
          "chi",
          "2026",
          "110888988",
          "1010759000",
          "179149000",
          "vay"
        ]
      },
      {
        "id": "chunk-monthly-report-2026-09-3",
        "headingPath": "Báo cáo tháng 2026-09 > Nguồn và nhận định",
        "text": "Nguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.",
        "keywords": [
          "sql",
          "monthly_pnl",
          "view",
          "truy",
          "sqlite",
          "khi",
          "trong",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "marketing-calendar",
    "docType": "marketing",
    "title": "Lịch marketing và cách đo",
    "period": "2026",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Lịch marketing và cách đo\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Lịch chiến dịch\n\n| Mã | Chiến dịch | Bắt đầu | Kết thúc | Ngân sách (VND) | Giảm giá (basis points) |\n|---|---|---|---|---:|---:|\n| C-BUNDLE | Bundle laptop và chuột | 2025-11-01 | 2025-11-30 | 24000000 | 200 |\n| C-TET | Ưu đãi trước Tết | 2026-01-15 | 2026-02-10 | 18000000 | 300 |\n| C-BTS | Tựu trường laptop văn phòng | 2026-08-01 | 2026-08-31 | 28000000 | 600 |\n\n## Phạm vi\n\nC-BTS giảm 6% chỉ cho laptop văn phòng; C-BUNDLE giảm 2%; C-TET giảm 3%. Không cộng dồn khuyến mãi. Doanh thu gắn campaign_id là doanh thu liên quan chiến dịch, không phải phần tăng thêm do quảng cáo. Không dùng ROAS để khẳng định lợi nhuận hoặc quan hệ nhân quả.",
    "chunks": [
      {
        "id": "chunk-marketing-calendar-1",
        "headingPath": "Lịch marketing và cách đo > Lịch marketing và cách đo",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "marketing",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-marketing-calendar-2",
        "headingPath": "Lịch marketing và cách đo > Lịch chiến dịch",
        "text": "| Mã | Chiến dịch | Bắt đầu | Kết thúc | Ngân sách (VND) | Giảm giá (basis points) |\n|---|---|---|---|---:|---:|\n| C-BUNDLE | Bundle laptop và chuột | 2025-11-01 | 2025-11-30 | 24000000 | 200 |\n| C-TET | Ưu đãi trước Tết | 2026-01-15 | 2026-02-10 | 18000000 | 300 |\n| C-BTS | Tựu trường laptop văn phòng | 2026-08-01 | 2026-08-31 | 28000000 | 600 |",
        "keywords": [
          "vnd",
          "tet",
          "bundle",
          "bts",
          "600",
          "points",
          "2026",
          "200"
        ]
      },
      {
        "id": "chunk-marketing-calendar-3",
        "headingPath": "Lịch marketing và cách đo > Phạm vi",
        "text": "C-BTS giảm 6% chỉ cho laptop văn phòng; C-BUNDLE giảm 2%; C-TET giảm 3%. Không cộng dồn khuyến mãi. Doanh thu gắn campaign_id là doanh thu liên quan chiến dịch, không phải phần tăng thêm do quảng cáo. Không dùng ROAS để khẳng định lợi nhuận hoặc quan hệ nhân quả.",
        "keywords": [
          "doanh",
          "tet",
          "bundle",
          "bts",
          "quan",
          "campaign_id",
          "cho",
          "roas"
        ]
      }
    ]
  },
  {
    "id": "pricing-policy",
    "docType": "policy",
    "title": "Quy định giá và biên gộp",
    "period": "2026",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-03-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Quy định giá và biên gộp\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Ràng buộc\n\nBiên lợi nhuận gộp tối thiểu cho laptop 5%, card đồ họa 4%, nhóm khác 10%. Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. Đây là ràng buộc đề xuất; không tự thực hiện giảm giá.",
    "chunks": [
      {
        "id": "chunk-pricing-policy-1",
        "headingPath": "Quy định giá và biên gộp > Quy định giá và biên gộp",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "quy",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-pricing-policy-2",
        "headingPath": "Quy định giá và biên gộp > Ràng buộc",
        "text": "Biên lợi nhuận gộp tối thiểu cho laptop 5%, card đồ họa 4%, nhóm khác 10%. Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. Đây là ràng buộc đề xuất; không tự thực hiện giảm giá.",
        "keywords": [
          "xem",
          "card",
          "cho",
          "khi",
          "laptop",
          "xin",
          "shop"
        ]
      }
    ]
  },
  {
    "id": "pricing-policy",
    "docType": "policy",
    "title": "Quy định giá và biên gộp",
    "period": "2026",
    "effectiveFrom": "2026-04-01",
    "effectiveTo": "2026-12-31",
    "version": "1.2",
    "status": "indexed",
    "content": "# Quy định giá và biên gộp\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Ràng buộc\n\nTừ 2026-04-01, biên gộp tối thiểu cho laptop 6%, card đồ họa 4%, nhóm khác 10%. Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. Kiểm tra biên sau giảm từ giá vốn FIFO; không hứa mức giá nếu chưa được duyệt.",
    "chunks": [
      {
        "id": "chunk-pricing-policy-1",
        "headingPath": "Quy định giá và biên gộp > Quy định giá và biên gộp",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "quy",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-pricing-policy-2",
        "headingPath": "Quy định giá và biên gộp > Ràng buộc",
        "text": "Từ 2026-04-01, biên gộp tối thiểu cho laptop 6%, card đồ họa 4%, nhóm khác 10%. Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. Kiểm tra biên sau giảm từ giá vốn FIFO; không hứa mức giá nếu chưa được duyệt.",
        "keywords": [
          "fifo",
          "xem",
          "card",
          "2026",
          "cho",
          "khi",
          "tra",
          "laptop"
        ]
      }
    ]
  },
  {
    "id": "procurement",
    "docType": "sales_plan",
    "title": "Quy trình nhập hàng",
    "period": "2026",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Quy trình nhập hàng\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Nhà cung cấp giả lập\n\nSUP-LAP có lead time 4 ngày, SUP-PC 3 ngày. Đơn nhập chưa nhận không tính là tồn kho; lấy receipts làm ngày tăng tồn. Mức đặt lại trong simulator: laptop 1 sản phẩm, nhóm khác 3; đặt lên 4 laptop hoặc 8 linh kiện. Các ngưỡng này là giả định mô phỏng, chưa tối ưu thực tế.\n\n## Hạch toán\n\nĐơn bán xuất FIFO. Hoàn có thể nhập lại kho hoặc không; chỉ đảo giá vốn nếu hàng bán lại được. Không xác nhận tương thích Build PC khi nguồn thiếu socket/kích thước/điện năng.",
    "chunks": [
      {
        "id": "chunk-procurement-1",
        "headingPath": "Quy trình nhập hàng > Quy trình nhập hàng",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "quy",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-procurement-2",
        "headingPath": "Quy trình nhập hàng > Nhà cung cấp giả lập",
        "text": "SUP-LAP có lead time 4 ngày, SUP-PC 3 ngày. Đơn nhập chưa nhận không tính là tồn kho; lấy receipts làm ngày tăng tồn. Mức đặt lại trong simulator: laptop 1 sản phẩm, nhóm khác 3; đặt lên 4 laptop hoặc 8 linh kiện. Các ngưỡng này là giả định mô phỏng, chưa tối ưu thực tế.",
        "keywords": [
          "kho",
          "simulator",
          "lap",
          "lead",
          "cung",
          "receipts",
          "linh",
          "trong"
        ]
      },
      {
        "id": "chunk-procurement-3",
        "headingPath": "Quy trình nhập hàng > Hạch toán",
        "text": "Đơn bán xuất FIFO. Hoàn có thể nhập lại kho hoặc không; chỉ đảo giá vốn nếu hàng bán lại được. Không xác nhận tương thích Build PC khi nguồn thiếu socket/kích thước/điện năng.",
        "keywords": [
          "fifo",
          "kho",
          "khi",
          "build",
          "socket"
        ]
      }
    ]
  },
  {
    "id": "positioning",
    "docType": "sales_plan",
    "title": "Định vị shop và giới hạn suy luận",
    "period": "2026",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Định vị shop và giới hạn suy luận\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Phân khúc\n\nMột điểm bán, 5 người kể cả chủ shop; tập trung laptop văn phòng, laptop gaming phổ thông và linh kiện nâng cấp. Bán tại cửa hàng, website và social. Chỉ nhận định sản phẩm bán chạy theo kỳ từ SQL, không gắn nhãn hot chỉ từ hãng. Không lấy doanh thu FPT Shop hoặc MWG làm doanh thu cửa hàng này.\n\n## Số liệu chưa đủ\n\nChưa mô hình hóa lãi vay, thuế thu nhập hay nghĩa vụ VAT; không kết luận lợi nhuận sau thuế. Cần dữ liệu thật để đánh giá dự báo và quyết định kinh doanh.",
    "chunks": [
      {
        "id": "chunk-positioning-1",
        "headingPath": "Định vị shop và giới hạn suy luận > Định vị shop và giới hạn suy luận",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "suy",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-positioning-2",
        "headingPath": "Định vị shop và giới hạn suy luận > Phân khúc",
        "text": "Một điểm bán, 5 người kể cả chủ shop; tập trung laptop văn phòng, laptop gaming phổ thông và linh kiện nâng cấp. Bán tại cửa hàng, website và social. Chỉ nhận định sản phẩm bán chạy theo kỳ từ SQL, không gắn nhãn hot chỉ từ hãng. Không lấy doanh thu FPT Shop hoặc MWG làm doanh thu cửa hàng này.",
        "keywords": [
          "theo",
          "doanh",
          "trung",
          "fpt",
          "sql",
          "hot",
          "laptop",
          "social"
        ]
      },
      {
        "id": "chunk-positioning-3",
        "headingPath": "Định vị shop và giới hạn suy luận > Số liệu chưa đủ",
        "text": "Chưa mô hình hóa lãi vay, thuế thu nhập hay nghĩa vụ VAT; không kết luận lợi nhuận sau thuế. Cần dữ liệu thật để đánh giá dự báo và quyết định kinh doanh.",
        "keywords": [
          "doanh",
          "vat",
          "vay",
          "kinh",
          "thu",
          "hay",
          "sau"
        ]
      }
    ]
  },
  {
    "id": "customer-policy",
    "docType": "policy",
    "title": "Chính sách dùng cho shop giả lập",
    "period": "2026",
    "effectiveFrom": "2025-10-01",
    "effectiveTo": "2026-12-31",
    "version": "1.1",
    "status": "indexed",
    "content": "# Chính sách dùng cho shop giả lập\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n## Đổi trả và bảo hành\n\nChính sách này chỉ dùng demo. Khi bán thật cần chủ shop duyệt điều kiện theo từng SKU. Không lấy thời hạn bảo hành của cửa hàng nước ngoài áp dụng cho shop Việt Nam. Khách muốn xác nhận bảo hành hoặc thanh toán cần liên hệ nhân viên.",
    "chunks": [
      {
        "id": "chunk-customer-policy-1",
        "headingPath": "Chính sách dùng cho shop giả lập > Chính sách dùng cho shop giả lập",
        "text": "DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.",
        "keywords": [
          "doanh",
          "cho",
          "kinh",
          "retail_sim_v1",
          "hay",
          "shop"
        ]
      },
      {
        "id": "chunk-customer-policy-2",
        "headingPath": "Chính sách dùng cho shop giả lập > Đổi trả và bảo hành",
        "text": "Chính sách này chỉ dùng demo. Khi bán thật cần chủ shop duyệt điều kiện theo từng SKU. Không lấy thời hạn bảo hành của cửa hàng nước ngoài áp dụng cho shop Việt Nam. Khách muốn xác nhận bảo hành hoặc thanh toán cần liên hệ nhân viên.",
        "keywords": [
          "theo",
          "thanh",
          "cho",
          "khi",
          "nam",
          "demo",
          "sku",
          "shop"
        ]
      }
    ]
  }
];
