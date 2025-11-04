import os
import asyncio
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-057Bd2801D88b71Ce3')

async def generate_hero():
    prompt = """Create a vibrant, professional hero image for 'GR8 AI AUTOMATION' platform.

Style: Modern, innovative, energetic with bright colors (teal #0c969b, blue, purple gradients)
Mood: Happy, dynamic, transformative, exciting

Main Elements:
- Large bold text 'GR8 AI AUTOMATION' prominently displayed in modern font
- Friendly AI robots/agents working together collaboratively  
- Network connections with glowing nodes and flowing data lines
- Central core hub with connections radiating outward
- Innovation symbols: lightbulbs glowing, sparkles, forward arrows
- Digital elements: chat bubbles, calendars, charts, email icons
- Sense of movement and energy
- Professional business aesthetic with vibrant colors

Composition: Centered text with dynamic elements surrounding it
Atmosphere: Optimistic, forward-thinking, transformative
Quality: Professional marketing material, high contrast, eye-catching"""
    
    try:
        image_gen = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=1
        )
        
        if images:
            path = "/app/frontend/public/gr8-hero.png"
            with open(path, "wb") as f:
                f.write(images[0])
            print(f"✅ Generated hero image: {path}")
            print(f"✅ Size: {len(images[0])/1024:.1f}KB")
            return path
        else:
            print("❌ No image generated")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_hero())
