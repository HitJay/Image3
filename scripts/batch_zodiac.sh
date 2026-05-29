#!/usr/bin/env bash
# Batch generate zodiac ink wash series
# Usage: bash scripts/batch_zodiac.sh
set -e
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env | xargs)

OUTPUT_DIR="./output/zodiac_ink"
mkdir -p "$OUTPUT_DIR"

declare -A PROMPTS
PROMPTS[zodiac_07_horse]='Chinese ink wash painting (水墨画), a cute young foal galloping joyfully across a meadow, flying mane and tail, energetic splashed ink technique inspired by Xu Beihong horses, chubby round body, dynamic motion, grass strokes in foreground, distant mountains in light wash, spirited and adorable, 3:4 aspect ratio'
PROMPTS[zodiac_08_goat]='Chinese ink wash painting (水墨画), three adorable fluffy baby lambs cuddling together (三阳开泰), soft curly wool, sweet gentle expressions, plum blossom branches above, early spring atmosphere, auspicious composition, traditional sumi-e with light color accents, warm and joyful mood, delicate brushwork, 3:4 aspect ratio'
PROMPTS[zodiac_09_monkey]='Chinese ink wash painting (水墨画), a mischievous cute baby monkey stealing peaches from a peach tree, one peach in mouth another in hand, cheeky grin, agile pose on branch, pink peach blossoms blooming, lively brushwork, playful splashed ink, Qi Baishi inspired style, humorous and energetic, 3:4 aspect ratio'
PROMPTS[zodiac_10_rooster]='Chinese ink wash painting (水墨画), a proud adorable rooster crowing at dawn, magnificent colorful tail feathers painted with splashed ink technique, bright red comb, standing on a rock near morning glory fence, sunrise golden light, vibrant yet traditional brushwork, bold ink strokes, rural charm, 3:4 aspect ratio'
PROMPTS[zodiac_11_dog]='Chinese ink wash painting (水墨画), an adorable chubby Chinese village puppy sitting beside a stone lion guardian at a traditional door, head tilted cutely, red lanterns hanging above, blue-grey brick wall, warm welcoming atmosphere, homey and nostalgic, sumi-e brushwork with touches of red and warm tones, 3:4 aspect ratio'
PROMPTS[zodiac_12_pig]='Chinese ink wash painting (水墨画), an extremely round and chubby cute piglet splashing playfully in a lotus pond, joyful expression, water droplets flying, surrounded by lotus flowers and large leaves, pink and green color accents on ink wash base, carefree happy mood, auspicious meaning, soft sumi-e brushwork, 3:4 aspect ratio'

for prefix in zodiac_07_horse zodiac_08_goat zodiac_09_monkey zodiac_10_rooster zodiac_11_dog zodiac_12_pig; do
    # Skip if already generated
    if compgen -G "$OUTPUT_DIR/${prefix}_*" > /dev/null 2>&1; then
        echo "  [skip] $prefix already exists"
        continue
    fi
    echo "=== Generating: $prefix ==="
    python3 scripts/generate.py \
        --provider matpool \
        --prompt "${PROMPTS[$prefix]}" \
        --width 768 --height 1024 \
        --output-dir "$OUTPUT_DIR" \
        --prefix "$prefix"
    echo ""
done

echo "=== All zodiac images complete! ==="
ls -la "$OUTPUT_DIR"/zodiac_*.png
