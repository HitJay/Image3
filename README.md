# Image3 — AI 图像生成工作台

基于 API 的 AI 图像生成项目，聚焦趣味图像、手机壁纸、小红书内容创作。

## 为什么用 API？

- **不挑硬件** — 8GB 显存也能跑最新模型（FLUX、GPT-Image-2 等）
- **零部署** — 不用装 ComfyUI、下模型，配好 API Key 直接出图
- **模型多** — 矩池云(MatPool) 提供 GPT-Image-2、FLUX、SD3.5 等
- **支持 img2img** — 以图生图、风格迁移、壁纸生成全支持

## 快速开始

### 1. 设置 API Key

```bash
# 方式一：环境变量
export IMAGE_API_KEY="your_matpool_api_key"

# 方式二：.env 文件
cp .env.example .env
# 编辑 .env，填入你的 key
```

### 2. 生成图片

```bash
# 最简单的用法
python3 scripts/generate.py --prompt "一只宇航员猫在太空站，数字艺术，4K"

# 用 prompt 模板
python3 scripts/generate.py --category creative --prompt-name cat_astronaut

# 随机抽一个 prompt
python3 scripts/generate.py --category wallpapers --random-prompt

# 批量生成 10 张
python3 scripts/generate.py --category wallpapers --prompt-name cyberpunk --count 10

# img2img 以图生图
python3 scripts/generate.py --prompt "make it watercolor painting" \
  --input-image ./photo.jpg --strength 0.5
```

### 3. 批量出图

```bash
# 批量壁纸（16:9）
python3 scripts/batch_wallpaper.py --theme cyberpunk --count 10

# 批量小红书内容（3:4 竖屏）
python3 scripts/batch_xhs.py --theme mood_board --count 12
```

### 4. 切换模型 / 供应商

```bash
# 指定模型
python3 scripts/generate.py --prompt "..." --model flux-1.1-pro

# 用 OpenAI DALL-E
python3 scripts/generate.py --provider openai --api-key sk-xxx --prompt "..."

# 自定义 API
python3 scripts/generate.py --provider custom \
  --api-base https://your-api.com --api-key xxx --model your-model \
  --prompt "..."
```

## 项目结构

```
Image3/
├── scripts/
│   ├── generate.py          # 主生成脚本（API + ComfyUI 双模式）
│   ├── batch_wallpaper.py   # 批量壁纸
│   └── batch_xhs.py         # 批量小红书
├── src/image3/
│   ├── api_client.py        # API 客户端（MatPool/OpenAI 兼容）
│   ├── client.py            # ComfyUI 本地客户端（可选）
│   └── prompts.py           # Prompt 模板管理
├── prompts/                 # 9 个精选 Prompt 模板
│   ├── wallpapers/          # 赛博朋克 / 自然 / 抽象
│   ├── creative/            # 猫宇航员 / 像素世界 / 秋叶狐狸
│   └── xiaohongshu/         # 情绪板 / 平铺 / 色彩研究
├── output/                  # 生成输出（gitignore）
└── tests/                   # 15 个测试
```

## 支持的后端

| 后端 | 方式 | 模型 |
|------|------|------|
| **MatPool (矩池云)** | API | GPT-Image-2, FLUX, SD3.5 |
| **OpenAI** | API | DALL-E 3 |
| **自定义 API** | API | 任何 OpenAI 兼容接口 |
| **ComfyUI 本地** | 本地 GPU | SDXL, FLUX GGUF, SD1.5 |

## Prompt 模板系统

`prompts/` 目录下按类别组织 `.txt` 模板：

```
prompts/
├── wallpapers/       # 壁纸：赛博朋克、自然风光、抽象几何
├── creative/         # 趣味：猫宇航员、像素世界、魔法生物
└── xiaohongshu/      # 小红书：情绪板、平铺摄影、色彩研究
```

新建一个模板就是新建一个 `.txt` 文件。

## License

MIT
