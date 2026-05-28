# Image3 — AI 图像生成工作台

基于 ComfyUI 的 AI 图像生成项目，聚焦趣味图像、手机壁纸、小红书内容创作。

## 模型策略

- **主力模型**: FLUX / SDXL (img2img + ControlNet)
- **轻量备选**: SD 1.5 (快速出图，适合草稿)
- **增强工具**: IP-Adapter (风格迁移), ControlNet (构图控制), Upscaler (高清放大)

## 项目结构

```
Image3/
├── workflows/          # ComfyUI 工作流 JSON（API 格式）
├── prompts/            # Prompt 模板库
│   ├── wallpapers/     # 壁纸类
│   ├── creative/       # 趣味创意
│   └── xiaohongshu/    # 小红书内容
├── output/             # 生成输出（不入 git）
├── scripts/            # 自动化脚本
├── src/image3/         # Python 工具库
├── config/             # 配置文件
└── tests/              # 测试
```

## 快速开始

### 1. 启动 ComfyUI

```bash
# 本地 ComfyUI（需先安装）
comfy launch --background

# 或手动启动
python main.py --listen 127.0.0.1 --port 8188
```

### 2. 生成图片

```bash
# txt2img
python scripts/generate.py --workflow workflows/txt2img.json \
  --args '{"prompt": "一只猫在太空站", "seed": -1}'

# img2img (以图生图)
python scripts/generate.py --workflow workflows/img2img.json \
  --input-image image=./input.jpg \
  --args '{"prompt": "watercolor painting style", "denoise": 0.6}'

# 批量壁纸
python scripts/batch_wallpaper.py --theme "cyberpunk" --count 10
```

### 3. 小红书发布流程

1. 选题 → 从 `prompts/xiaohongshu/` 选模板
2. 批量生成 → `scripts/batch_xhs.py --theme xxx --count 20`
3. 挑选 → 人工筛选 6-9 张
4. 排版 → 可直接用/加小红书模板边框

## 硬件要求

- NVIDIA GPU ≥ 8GB VRAM (SDXL) 或 ≥ 12GB (FLUX)
- 或 ComfyUI Cloud (RTX 6000 Pro, 付费)

## License

MIT
