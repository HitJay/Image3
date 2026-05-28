# 浮世绘猫 · Ukiyo-e Cats

> AI生成浮世绘风格猫咪头像合集 · 6张 · ¥9.9
> 复旦杰伦@小红书 · 2026-05-29

## 文件结构

```
output/ukiyo_cats/
├── catalog.json          ← 完整目录（JSON，方便程序检索）
├── cover.html            ← 封面HTML（自包含，浏览器打开截图）
├── watermarked/          ← 加水印原图（百度网盘发货用）
│   ├── ukiyo_*_000.png   ← 6张，右下角「复旦杰伦@小红书」
├── cards/                ← 小红书轮播卡片（可直接发）
│   ├── 01_浮世绘猫.png   ← 封面 ¥9.9/6张
│   ├── 02_慵懒午后.png
│   ├── 03_月下暗影.png
│   ├── 04_一叶知秋.png
│   ├── 05_紫藤嬉戏.png
│   ├── 06_月下独酌.png
│   └── 文案.txt           ← 小红书正文
└── [6原图].png           ← 未加水印原图（保留）
```

## 6张图一览

| # | 主题 | 英文 | 内容 |
|---|------|------|------|
| 1 | 慵懒午后 | Lazy Afternoon | 橘猫午睡 · 障子门 · 锦鲤池 |
| 2 | 月下暗影 | Moonlit Shadow | 黑猫夜巡 · 新月 · 松影 |
| 3 | 一叶知秋 | Autumn Leaf | 白猫扑枫叶 · 鸟居 · 秋色 |
| 4 | 紫藤嬉戏 | Wisteria Play | 双猫闹紫藤 · 石灯笼 |
| 5 | 浮世绘猫 | Ukiyo-e Cat | 三花猫骑锦鲤 · 巨浪 |
| 6 | 月下独酌 | Moonlit Solitude | 灰猫望月 · 茶杯 · 樱花 |

## 复现命令

```bash
cd /mnt/d/vscode/Image3
source .env

# 单张生成
python3 scripts/generate.py --provider matpool --model Nano-Banana-Spot   --prompt "Japanese ukiyo-e woodblock print, ..."   --width 768 --height 1024 --output-dir ./output/xxx

# 批量（prompt 模板在 prompts/ukiyo_cats/）
for f in prompts/ukiyo_cats/*.md; do
  prompt=$(grep -A1 "^\*\*生成 Prompt：\*\*" "$f" | tail -1)
  python3 scripts/generate.py --prompt "$prompt" ...
done
```

## Prompt 模板

详见 `prompts/ukiyo_cats/` 目录，每张图一个 `.md` 文件，含中英文描述 + 完整 prompt。
