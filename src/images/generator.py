from PIL import Image, ImageDraw, ImageFont
import os

class SignalCardGenerator:
    def __init__(self, config):
        self.config = config['telegram']
        self.width = 1000
        self.height = 700
        self.bg_color = (15, 18, 25) # Ultra Dark theme
        self.text_color = (240, 240, 240)
        self.accent_color = (0, 255, 180) # Ultra Green
        self.sell_color = (255, 60, 60) # Ultra Red
        self.brand_color = (255, 215, 0) # Gold for Premium branding

    def generate_card(self, signal_data, output_path, df=None):
        import matplotlib.pyplot as plt
        import io
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 1. Create Chart if data provided
        if df is not None:
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(12, 7))
            ax.plot(df['timestamp'], df['close'], color='#00FFB4', linewidth=2, alpha=0.8)
            ax.fill_between(df['timestamp'], df['close'], df['close'].min(), color='#00FFB4', alpha=0.1)
            
            # Entry/SL/TP Lines with better colors
            ax.axhline(y=signal_data['entry_price'], color='#FFD700', linestyle='-', linewidth=1.5, label='ENTRY')
            ax.axhline(y=signal_data['stop_loss'], color='#FF3C3C', linestyle='-', linewidth=1.5, label='STOP LOSS')
            ax.axhline(y=signal_data['tp1'], color='#00FFB4', linestyle='-', linewidth=1.5, label='TARGET 1')
            
            ax.set_facecolor('#0F1219')
            ax.grid(color='#2D3436', linestyle='--', alpha=0.3)
            ax.set_title(f"{signal_data['coin']} | ULTRA SIGNAL", color='white', fontsize=16, fontweight='bold')
            ax.legend(facecolor='#0F1219', edgecolor='#2D3436')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            chart_img = Image.open(buf).resize((550, 400))
            plt.close()

        # 2. Create the Card
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        color = self.accent_color if signal_data['direction'] == "BUY" else self.sell_color
        
        # Header & Details
        draw.rectangle([0, 0, self.width, 120], fill=(25, 30, 40))
        draw.text((50, 40), f"💎 ULTRA PREMIUM SIGNAL: {signal_data['coin']}", fill=self.brand_color)
        
        # Paste Chart with border
        if df is not None:
            draw.rectangle([395, 145, 955, 555], outline=(45, 50, 60), width=2)
            img.paste(chart_img, (400, 150))

        # Details with icons
        y_offset = 180
        details = [
            f"📊 DIRECTION: {signal_data['direction']}",
            f"🎯 ENTRY: {signal_data['entry_price']:.5f}",
            f"🛑 STOP LOSS: {signal_data['stop_loss']:.5f}",
            f"✅ TARGET 1: {signal_data['tp1']:.5f}",
            f"✅ TARGET 2: {signal_data['tp2']:.5f}",
            f"✅ TARGET 3: {signal_data['tp3']:.5f}",
            f"📈 SCORE: {signal_data['confidence']}%",
            f"⚖️ RISK/REWARD: {signal_data['risk_reward']}"
        ]
        
        for detail in details:
            draw.text((50, y_offset), detail, fill=self.text_color)
            y_offset += 55
            
        # Footer
        draw.rectangle([0, 620, self.width, self.height], fill=(25, 30, 40))
        draw.text((50, 645), f"🔗 {self.config['watermark']} | 🏆 {self.config['channel_branding']}", fill=self.brand_color)
        img.save(output_path)
        return output_path
