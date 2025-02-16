import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind  # 引入 t 檢定

def remove_outliers_iqr(data):
    """
    利用 IQR 方法移除離群值。
    當資料量不足（小於 4 筆）時，直接回傳原資料。
    """
    if len(data) < 4:
        return data
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    filtered = [x for x in data if lower_bound <= x <= upper_bound]
    return filtered

def analyze_scores(root_directory, remove_outliers=True):
    """
    遍歷指定資料夾，讀取 summary_scores.csv，
    並依據問卷名稱收集各測驗分數。
    
    若 remove_outliers 為 True，則利用 IQR 方法剔除離群值。
    
    同時，若單一參與者的「飛鳥前測」、「飛鳥後測」與「音樂後測」
    分數皆存在且三者數值均相同，則捨棄該參與者的所有資料。
    """
    # 用於存儲各測驗的所有分數
    scores = {
        '飛鳥前測': [],
        '飛鳥後測': [],
        '音樂後測': []
    }
    
    # 遍歷所有資料夾
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if 'summary_scores.csv' in filenames:
            file_path = os.path.join(dirpath, 'summary_scores.csv')
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                participant_scores = {}
                # 收集單一參與者的各測驗分數
                for index, row in df.iterrows():
                    if row['問卷名稱'] in scores:
                        participant_scores[row['問卷名稱']] = row['總分']
                        
                # 若該參與者擁有三項測驗且三者分數均相同，則跳過該參與者的所有資料
                if len(participant_scores) == 3 and len(set(participant_scores.values())) == 1:
                    continue
                else:
                    for quiz, score in participant_scores.items():
                        scores[quiz].append(score)
            except Exception as e:
                print(f"處理檔案 {file_path} 時發生錯誤: {e}")
    
    # 計算統計數據
    statistics = {
        'names': [],
        'means': [],
        'medians': [],
        'q1': [],
        'q3': [],
        'mins': [],
        'maxs': [],
        'counts': [],
        'data': []
    }
    
    # 對每一個問卷類別進行統計，並依需求進行離群值剔除
    for name, values in scores.items():
        if values:
            filtered_values = remove_outliers_iqr(values) if remove_outliers else values
            statistics['names'].append(name)
            statistics['means'].append(np.mean(filtered_values))
            statistics['medians'].append(np.median(filtered_values))
            statistics['q1'].append(np.percentile(filtered_values, 25))
            statistics['q3'].append(np.percentile(filtered_values, 75))
            statistics['mins'].append(np.min(filtered_values))
            statistics['maxs'].append(np.max(filtered_values))
            statistics['counts'].append(len(filtered_values))
            statistics['data'].append(filtered_values)
    
    return statistics

def get_significance_marker(p_val):
    """根據 p 值返回對應的顯著性標記"""
    if p_val < 0.001:
        return '***'
    elif p_val < 0.01:
        return '**'
    elif p_val < 0.05:
        return '*'
    else:
        return ''

def plot_scores_with_boxplot(statistics, custom_labels=None):
    """
    利用 matplotlib 繪製箱形圖，並標示原始數據與 t 檢定結果。
    這裡對 1-2、1-3 及 2-3 三組都做 t 檢定。
    """
    plt.figure(figsize=(10, 6))
    
    # 設置中文字體
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 若 custom_labels 不為 None 且數量正確，則使用自定義標籤
    if custom_labels is not None and len(custom_labels) == len(statistics['names']):
        x_labels = custom_labels
    else:
        x_labels = statistics['names']
    
    # 繪製箱形圖
    box_plot = plt.boxplot(statistics['data'], 
                           labels=x_labels,
                           patch_artist=True,
                           medianprops={'color': 'black', 'linewidth': 1.5},
                           flierprops={'marker': 'o', 'markerfacecolor': 'gray'},
                           boxprops={'facecolor': 'lightblue', 'alpha': 0.5},
                           showfliers=False)  # 不顯示離群點（另以散點顯示）
    
    # 添加散點圖顯示原始數據（並加上隨機偏移避免重疊）
    for i, data in enumerate(statistics['data']):
        x = np.random.normal(i+1, 0.04, size=len(data))
        plt.scatter(x, data, alpha=0.6, c='red', s=30)
    
    # 在箱形圖上標註平均值
    for i, mean in enumerate(statistics['means']):
        plt.text(i+1, mean, f'平均: {mean:.2f}', ha='center', va='bottom')
    
    # ---------------------------
    # 進行 t 檢定
    # 組別索引：0 = 飛鳥前測 (base), 1 = 飛鳥後測 (stress), 2 = 音樂後測 (music)
    # 1 vs 2
    t_stat_1_2, p_val_1_2 = ttest_ind(statistics['data'][0], statistics['data'][1], equal_var=False)
    sig_marker_1_2 = get_significance_marker(p_val_1_2)
    # 1 vs 3
    t_stat_1_3, p_val_1_3 = ttest_ind(statistics['data'][0], statistics['data'][2], equal_var=False)
    sig_marker_1_3 = get_significance_marker(p_val_1_3)
    # 2 vs 3
    t_stat_2_3, p_val_2_3 = ttest_ind(statistics['data'][1], statistics['data'][2], equal_var=False)
    sig_marker_2_3 = get_significance_marker(p_val_2_3)
    
    # ---------------------------
    # 設置圖表標題、座標軸標籤及網格
    plt.title('合併', fontsize=14)
    plt.xlabel('階段', fontsize=12)
    plt.ylabel('分數', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 設定固定的縱軸範圍，並增加空間以便標示統計檢定結果
    plt.ylim(0, 15)
    
    # ---------------------------
    # 標示 t 檢定結果（利用水平線與文字標示）
    # 組別 1 vs 組別 2 (x=1 與 x=2)
    y0 = 11.5  # 調整位置
    plt.plot([1, 1, 2, 2], [y0, y0+0.5, y0+0.5, y0], lw=1.5, c='black')
    plt.text(1.5, y0+0.5, f"p={p_val_1_2:.3f}, t={t_stat_1_2:.2f}{sig_marker_1_2}", 
             ha='center', va='bottom')
    
    # 組別 1 vs 組別 3 (x=1 與 x=3)
    y1 = 12.5  # 調整位置
    plt.plot([1, 1, 3, 3], [y1, y1+0.5, y1+0.5, y1], lw=1.5, c='black')
    plt.text(2, y1+0.5, f"p={p_val_1_3:.3f}, t={t_stat_1_3:.2f}{sig_marker_1_3}", 
             ha='center', va='bottom')
    
    # 組別 2 vs 組別 3 (x=2 與 x=3)
    y2 = 13.5  # 調整位置
    plt.plot([2, 2, 3, 3], [y2, y2+0.5, y2+0.5, y2], lw=1.5, c='black')
    plt.text(2.5, y2+0.5, f"p={p_val_2_3:.3f}, t={t_stat_2_3:.2f}{sig_marker_2_3}", 
             ha='center', va='bottom')
    
    # 調整整體布局
    plt.tight_layout()
    
    return plt

def main():
    root_directory = "merge"  # 資料夾路徑
    
    # 分析數據時啟用離群值剔除 (remove_outliers=True)
    statistics = analyze_scores(root_directory, remove_outliers=True)
    
    # 自定義 x 軸標籤（順序需與統計資料一致）
    custom_labels = ['base', 'stress', 'music']
    
    # 繪製圖表並傳入自定義標籤
    plt_obj = plot_scores_with_boxplot(statistics, custom_labels=custom_labels)
    
    # 儲存圖表
    plt_obj.savefig('合併.png', dpi=300, bbox_inches='tight')
    
    # 顯示圖表
    plt_obj.show()
    
    # 輸出數值統計結果
    print("\n數值統計結果：")
    for i, name in enumerate(statistics['names']):
        print(f"{name}:")
        print(f"  樣本數(n): {statistics['counts'][i]}")
        print(f"  平均值: {statistics['means'][i]:.2f}")
        print(f"  中位數: {statistics['medians'][i]:.2f}")
        print(f"  第一四分位數(Q1): {statistics['q1'][i]:.2f}")
        print(f"  第三四分位數(Q3): {statistics['q3'][i]:.2f}")
        print(f"  最小值: {statistics['mins'][i]:.2f}")
        print(f"  最大值: {statistics['maxs'][i]:.2f}")
        print()

if __name__ == "__main__":
    main()
