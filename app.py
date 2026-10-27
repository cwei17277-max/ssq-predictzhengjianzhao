import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
import io

# 设置页面配置
st.set_page_config(
    page_title="AI 证件照 DIY 助手",
    page_icon="📷",
    layout="centered"
)

# 页面标题与简介
st.title("📷 AI 证件照 DIY 助手")
st.markdown("上传普通生活照，一键完成 **AI 抠图**、**更换底色** 与 **裁剪标准尺寸**！")

# 1. 定义标准证件照尺寸 (宽 x 高，单位：像素，按300 DPI计算)
SIZE_DICT = {
    "一寸 (295 x 413 px)": (295, 413),
    "大一寸 (390 x 567 px)": (390, 567),
    "二寸 (413 x 579 px)": (413, 579),
    "小二寸/国考 (354 x 472 px)": (354, 472),
}

# 2. 定义底色对应的 RGB 颜色
COLOR_DICT = {
    "白色 (纯洁/常规)": (255, 255, 255),
    "蓝色 (工作/毕业)": (67, 142, 219),
    "红色 (结婚/节日)": (255, 0, 0),
}

# 侧边栏参数选择
st.sidebar.header("⚙️ 证件照参数设置")
selected_size_name = st.sidebar.selectbox("选择尺寸", list(SIZE_DICT.keys()))
selected_color_name = st.sidebar.selectbox("选择底色", list(COLOR_DICT.keys()))

target_size = SIZE_DICT[selected_size_name]
target_color = COLOR_DICT[selected_color_name]

# 3. 核心图像处理函数
def process_id_photo(input_image, size, background_color):
    # 步骤 A: AI 抠图，去除背景（返回带透明通道的 RGBA 图像）
    with st.spinner("AI 正在疯狂抠图中，请稍候..."):
        no_bg_image = remove(input_image)
    
    # 步骤 B: 智能裁剪与缩放以适应目标证件照比例 (保持人物居中且不拉伸)
    # 使用 PIL 的 fit 方法，自动居中裁剪
    cropped_image = ImageOps.fit(no_bg_image, size, method=Image.Resampling.LANCZOS)
    
    # 步骤 C: 创建目标颜色的纯色背景底图
    bg_image = Image.new("RGBA", size, background_color + (255,))
    
    # 步骤 D: 将抠好的人像图层粘在纯色背景上
    final_image = Image.alpha_composite(bg_image, cropped_image)
    
    # 转回 RGB 格式以便保存为常规的 JPG/PNG
    return final_image.convert("RGB")

# 4. 上传文件逻辑
uploaded_file = st.file_uploader("请上传一张正面清晰头像照...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 读取上传的图片
    input_img = Image.open(uploaded_file)
    
    # 展示原图与预览结果的左右布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 原始照片")
        st.image(input_img, use_container_width=True)
        
    with col2:
        st.subheader("✨ 预览生成")
        # 执行处理
        result_img = process_id_photo(input_img, target_size, target_color)
        st.image(result_img, use_container_width=True)
        
        # 5. 将处理好的图片转为二进制流，供用户下载
        buffer = io.BytesIO()
        result_img.save(buffer, format="JPEG", quality=95)
        byte_im = buffer.getvalue()
        
        st.download_button(
            label="💾 下载高清证件照",
            data=byte_im,
            file_name="my_id_photo.jpg",
            mime="image/jpeg",
            type="primary"
        )
