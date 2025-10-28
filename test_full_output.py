"""
完整顯示塔羅 API 輸出的測試腳本
"""
import requests
import json

BASE_URL = "http://localhost:8081"

print("=" * 80)
print("🔮 塔羅牌解讀測試 - 完整輸出版本")
print("=" * 80)
print()

# 測試資料
test_cases = [
    {"card": "太陽", "orientation": "upright"},
    {"card": "愚者", "orientation": "upright"},
    {"card": "月亮", "orientation": "reversed"},
]

for i, test_data in enumerate(test_cases, 1):
    print(f"{'=' * 80}")
    print(f"測試 {i}: {test_data['card']} - {'正位' if test_data['orientation'] == 'upright' else '逆位'}")
    print(f"{'=' * 80}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/tarot",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📋 卡牌: {data['card']}")
            print(f"🔄 方向: {data['orientation']}")
            print(f"📏 長度: {len(data['analysis'])} 字")
            print()
            print("🔮 完整解讀:")
            print("-" * 80)
            print(data['analysis'])
            print("-" * 80)
            print()
            print("✅ 測試成功")
        else:
            print(f"❌ 錯誤: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    
    print()
    print()

print("=" * 80)
print("🎉 所有測試完成!")
print("=" * 80)
