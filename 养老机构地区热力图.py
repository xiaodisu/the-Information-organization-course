import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel("上海市.xlsx")

# 处理缺失值
df = df.dropna(subset=['GCJ02经度', 'GCJ02纬度'])
df['GCJ02经度'] = pd.to_numeric(df['GCJ02经度'], errors='coerce')
df['GCJ02纬度'] = pd.to_numeric(df['GCJ02纬度'], errors='coerce')
df['床位数'] = pd.to_numeric(df.get('床位数', 0), errors='coerce').fillna(0)

# 创建热力图
shanghai_center = [31.2304, 121.4737]
m = folium.Map(location=shanghai_center, zoom_start=11, tiles='CartoDB positron')

# 添加热力图层
heat_data = []
for _, row in df.iterrows():
    if not pd.isna(row['GCJ02纬度']) and not pd.isna(row['GCJ02经度']):
        weight = min(1.0, max(0.1, row['床位数'] / 500)) if row['床位数'] > 0 else 0.1
        heat_data.append([row['GCJ02纬度'], row['GCJ02经度'], weight])

if heat_data:
    HeatMap(
        heat_data,
        radius=25,
        blur=15,
        gradient={0.1: 'blue', 0.5: 'lime', 0.9: 'red'},
        min_opacity=0.5,
        max_val=1.0
    ).add_to(m)

# 添加标记
for _, row in df.iterrows():
    if not pd.isna(row['GCJ02纬度']) and not pd.isna(row['GCJ02经度']):
        try:
            # 自定义弹出窗口样式
            popup_content = f"""
            <div style="
                width: 300px;  /* 增加宽度 */
                font-family: Arial, sans-serif;
                font-size: 12px;  /* 减小字体大小 */
                line-height: 1.4;
            ">
                <h3 style="
                    margin: 0 0 8px 0;
                    padding: 0;
                    font-size: 14px;
                    color: #2c3e50;
                ">{row.get('机构名称', '未知机构')}</h3>

                <table style="width:100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 3px; border-bottom: 1px solid #eee; font-weight: bold; width: 25%;">地址</td>
                        <td style="padding: 3px; border-bottom: 1px solid #eee;">{row.get('地址', '未知')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px; border-bottom: 1px solid #eee; font-weight: bold;">性质</td>
                        <td style="padding: 3px; border-bottom: 1px solid #eee;">{row.get('机构性质', '未知')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px; border-bottom: 1px solid #eee; font-weight: bold;">床位数</td>
                        <td style="padding: 3px; border-bottom: 1px solid #eee;">{int(row['床位数'])}</td>
                    </tr>
                    <tr>
                        <td style="padding: 3px; font-weight: bold;">联系电话</td>
                        <td style="padding: 3px;">{row.get('联系电话', '未知')}</td>
                    </tr>
                </table>
            </div>
            """

            # 创建弹出窗口对象
            popup = folium.Popup(
                folium.Html(popup_content, script=True),
                max_width=350  # 增加最大宽度
            )

            # 控制标记大小
            beds = row['床位数'] if row['床位数'] > 0 else 1
            radius = max(3, min(20, beds / 30))

            # 添加标记
            folium.CircleMarker(
                location=[row['GCJ02纬度'], row['GCJ02经度']],
                radius=radius,
                popup=popup,  # 使用自定义的弹出窗口
                color='#3186cc',
                fill=True,
                fill_opacity=0.7,
                weight=1
            ).add_to(m)
        except Exception as e:
            print(f"无法添加标记: {e}")

# 添加图层控制
folium.LayerControl().add_to(m)

# 保存地图
m.save('index.html')
print("地图已保存为 'index.html'")
