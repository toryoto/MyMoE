import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from django.conf import settings
from PIL import Image, ImageDraw

def _wrap_text(canvas_obj, text, font_name, font_size, max_width):
    """テキストを指定幅で折り返し"""
    words = text.split()
    lines = []
    current_line = ''
    
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if canvas_obj.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def generate_employee_profile_pdf(profile):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    font_path = os.path.join(settings.BASE_DIR, 'employees', 'static', 'fonts', 'NotoSansJP-Regular.ttf')
    
    try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('NotoSans', font_path))
            font_name = 'NotoSans'
        else:
            font_name = 'Helvetica'
    except:
        font_name = 'Helvetica'
    
    # モダンなグラデーション背景
    p.setFillColor(HexColor('#f8fafc'))
    p.rect(0, 0, width, height, fill=1, stroke=0)
    
    p.setFillColor(HexColor('#1e293b'))
    p.rect(0, height - 8*cm, width, 8*cm, fill=1, stroke=0)
    
    p.setFillColor(HexColor('#3b82f6'))
    p.rect(0, height - 0.5*cm, width, 0.5*cm, fill=1, stroke=0)
    
    photo_x = 3*cm
    photo_y = height - 5*cm
    photo_radius = 1.5*cm
    
    p.setFillColor(HexColor('#ffffff'))
    p.circle(photo_x, photo_y, photo_radius, fill=1, stroke=0)
    
    # プロフィール画像またはイニシャル
    if profile.photo and os.path.exists(profile.photo.path):
        try:
            img = Image.open(profile.photo.path)
            img = img.convert('RGBA')
            
            # 画像を正方形にリサイズ
            size = int(photo_radius * 2 * 72 / 2.54)  # Convert cm to pixels (assuming 72 DPI)
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # 円形マスクを作成
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # マスクを適用
            img.putalpha(mask)
            
            # 一時的にファイルに保存
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_circular_image.png')
            img.save(temp_path, 'PNG')
            
            # 円形に切り抜いた画像を描画
            img_draw_x = photo_x - photo_radius
            img_draw_y = photo_y - photo_radius
            
            p.drawImage(temp_path, img_draw_x, img_draw_y, width=photo_radius*2, height=photo_radius*2, mask='auto')
            
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            # 画像読み込み失敗時はイニシャルを表示
            p.setFillColor(HexColor('#3b82f6'))
            p.setFont(font_name, 36)
            initial = profile.user.username[0].upper() if profile.user.username else 'U'
            initial_width = p.stringWidth(initial, font_name, 36)
            p.drawString(photo_x - initial_width/2, photo_y - 0.5*cm, initial)
    else:
        p.setFillColor(HexColor('#3b82f6'))
        p.setFont(font_name, 36)
        initial = profile.user.username[0].upper() if profile.user.username else 'U'
        initial_width = p.stringWidth(initial, font_name, 36)
        p.drawString(photo_x - initial_width/2, photo_y - 0.5*cm, initial)
    
    name_x = photo_x + photo_radius + 1*cm
    
    p.setFillColor(HexColor('#ffffff'))
    p.setFont(font_name, 28)
    name = profile.user.get_full_name() or profile.user.username
    p.drawString(name_x, photo_y + 0.5*cm, name)
    
    p.setFillColor(HexColor('#94a3b8'))
    p.setFont(font_name, 16)
    p.drawString(name_x, photo_y, f"@{profile.user.username}")
    
    card_y = height - 10*cm
    card_height = 15*cm
    
    shadow_offset = 0.1*cm
    p.setFillColor(HexColor('#e2e8f0'))
    p.roundRect(2*cm + shadow_offset, card_y - card_height - shadow_offset, 
               width - 4*cm, card_height, 1*cm, fill=1, stroke=0)
    
    p.setFillColor(HexColor('#ffffff'))
    p.roundRect(2*cm, card_y - card_height, width - 4*cm, card_height, 1*cm, fill=1, stroke=0)
    
    content_x = 3*cm
    content_y = card_y - 2*cm
    
    p.setFillColor(HexColor('#1e293b'))
    p.setFont(font_name, 20)
    p.drawString(content_x, content_y, "基本情報")
    
    p.setStrokeColor(HexColor('#3b82f6'))
    p.setLineWidth(2)
    p.line(content_x, content_y - 0.3*cm, content_x + 4*cm, content_y - 0.3*cm)
    
    field_y = content_y - 1.5*cm
    
    fields = [
        ('電話番号', profile.phone_number or '未設定'),
        ('生年月日', str(profile.date_of_birth) if profile.date_of_birth else '未設定'),
        ('メールアドレス', profile.user.email or '未設定'),
        ('部署', profile.user.department.name if profile.user.department else '未設定'),
        ('DTE', profile.user.dte.name if profile.user.dte else '未設定'),
    ]
    
    for label, value in fields:
        p.setFillColor(HexColor('#64748b'))
        p.setFont(font_name, 12)
        p.drawString(content_x, field_y, label)
        
        p.setFillColor(HexColor('#1e293b'))
        p.setFont(font_name, 14)
        p.drawString(content_x + 4*cm, field_y, value)
        
        field_y -= 1*cm
    
    if profile.bio:
        bio_y = field_y - 1*cm
        
        p.setFillColor(HexColor('#1e293b'))
        p.setFont(font_name, 20)
        p.drawString(content_x, bio_y, "自己紹介")
        
        p.setStrokeColor(HexColor('#3b82f6'))
        p.setLineWidth(2)
        p.line(content_x, bio_y - 0.3*cm, content_x + 4*cm, bio_y - 0.3*cm)
        
        bio_text_y = bio_y - 1*cm
        p.setFillColor(HexColor('#475569'))
        p.setFont(font_name, 12)
        
        max_width = width - 6*cm
        bio_lines = _wrap_text(p, profile.bio, font_name, 12, max_width)
        
        for line in bio_lines:
            p.drawString(content_x, bio_text_y, line)
            bio_text_y -= 0.6*cm
        
        field_y = bio_text_y - 1*cm
    
    if profile.skills.all():
        skills_y = field_y - 1*cm
        
        p.setFillColor(HexColor('#1e293b'))
        p.setFont(font_name, 20)
        p.drawString(content_x, skills_y, "スキル")
        
        p.setStrokeColor(HexColor('#3b82f6'))
        p.setLineWidth(2)
        p.line(content_x, skills_y - 0.3*cm, content_x + 4*cm, skills_y - 0.3*cm)
        
        skill_x = content_x
        skill_y = skills_y - 1.2*cm
        
        for skill in profile.skills.all():
            skill_width = p.stringWidth(skill.name, font_name, 11) + 1*cm
            skill_height = 0.8*cm
            
            if skill_x + skill_width > width - 3*cm:
                skill_x = content_x
                skill_y -= 1.2*cm
            
            p.setFillColor(HexColor('#eff6ff'))
            p.roundRect(skill_x, skill_y - skill_height/2, skill_width, skill_height, 0.4*cm, fill=1, stroke=0)
            
            p.setFillColor(HexColor('#1d4ed8'))
            p.setFont(font_name, 11)
            p.drawString(skill_x + 0.5*cm, skill_y - 0.1*cm, skill.name)
            
            skill_x += skill_width + 0.5*cm
        
        field_y = skill_y - 1.5*cm # Adjust field_y after skills
    
    # Pre-Employment History Section
    if profile.pre_employment_histories.all():
        history_y = field_y - 1*cm
        
        # Check if new page is needed for history section
        if history_y < 5*cm: # Arbitrary threshold, adjust as needed
            p.showPage()
            history_y = height - 3*cm # Start from top of new page
        
        p.setFillColor(HexColor('#1e293b'))
        p.setFont(font_name, 20)
        p.drawString(content_x, history_y, "職歴")
        
        p.setStrokeColor(HexColor('#3b82f6'))
        p.setLineWidth(2)
        p.line(content_x, history_y - 0.3*cm, content_x + 4*cm, history_y - 0.3*cm)
        
        history_item_y = history_y - 1.5*cm
        
        for history in profile.pre_employment_histories.all().order_by('-end_date'):
            # Check for page break before drawing new history item
            if history_item_y < 5*cm: # If less than 5cm from bottom, start new page
                p.showPage()
                history_item_y = height - 3*cm # Reset y to top of new page
                
                # Redraw section title on new page if it was split
                p.setFillColor(HexColor('#1e293b'))
                p.setFont(font_name, 20)
                p.drawString(content_x, history_item_y, "職歴 (続き)")
                p.setStrokeColor(HexColor('#3b82f6'))
                p.setLineWidth(2)
                p.line(content_x, history_item_y - 0.3*cm, content_x + 4*cm, history_item_y - 0.3*cm)
                history_item_y -= 1.5*cm # Adjust for title
            
            p.setFillColor(HexColor('#1e293b'))
            p.setFont(font_name, 16)
            p.drawString(content_x, history_item_y, f"{history.job_title} at {history.company_name}")
            history_item_y -= 0.7*cm
            
            p.setFillColor(HexColor('#64748b'))
            p.setFont(font_name, 12)
            p.drawString(content_x, history_item_y, f"{history.start_date} - {history.end_date}")
            history_item_y -= 0.7*cm
            
            if history.job_description:
                p.setFillColor(HexColor('#475569'))
                p.setFont(font_name, 12)
                desc_lines = _wrap_text(p, history.job_description, font_name, 12, width - 6*cm)
                for line in desc_lines:
                    p.drawString(content_x, history_item_y, line)
                    history_item_y -= 0.6*cm
            
            history_item_y -= 1*cm # Space between history items
    
    footer_y = 2*cm
    p.setFillColor(HexColor('#94a3b8'))
    p.setFont(font_name, 10)
    footer_text = f"Generated on {profile.user.date_joined.strftime('%Y-%m-%d')}"
    footer_width = p.stringWidth(footer_text, font_name, 10)
    p.drawString((width - footer_width) / 2, footer_y, footer_text)
    
    p.showPage()
    p.save()
    
    return buffer.getvalue()
