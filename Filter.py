# !!!
from Config import *


def filter_and_rank(df):
    """
    通过财务因子设置过滤条件
    :param df: 原始数据
    :return: 返回 通过财务因子过滤并叠加量价因子的df
    """
    # # #===120日涨跌幅（120日内涨幅大的和120日内跌幅大的股票删掉
    df['120日累计涨跌幅_排名'] = df.groupby(['交易日期'])['120日累计涨跌幅'].rank(ascending=False, pct=True)
    # 排除120天（类似4个月）涨的最好和跌的最多的
    # condition = (df['120日累计涨跌幅_排名'] > 0.1)
    # condition &= (df['120日累计涨跌幅_排名'] < 0.9)

    df['归母ROE(ttm)_分位数'] = df.groupby(['交易日期'])['归母ROE(ttm)'].rank(ascending=False, pct=True)
    condition = (df['归母ROE(ttm)_分位数'] > 0.05)
    condition &= (df['归母ROE(ttm)_分位数'] <= 0.35)

    df['毛利率_分位数'] = df.groupby(['交易日期'])['毛利率(ttm)'].rank(ascending=False, pct=True)
    # condition &= (df['毛利率_分位数'] > 0)
    condition &= (df['毛利率_分位数'] <= 0.9)

    # 新增速动比率
    df['速动比率_分位数'] = df.groupby(['交易日期'])['速动比率'].rank(ascending=False, pct=True)
    condition &= (df['速动比率_分位数'] >= 0.6)
    condition &= (df['速动比率_分位数'] <= 0.77)

    df = df[condition]  # 综上所有财务因子的过滤条件，选股
    # 定义需要进行rank的因子
    factors_rank_dict = {
        '归母ROE(ttm)_分位数': False,
        '毛利率_分位数': False,
        '总市值': True,
        '换手率': True,
    }

    # 定义合并需要的list
    merge_factor_list = []
    # 遍历factors_rank_dict进行排序
    for factor in factors_rank_dict:
        df[factor + '_rank'] = df.groupby('交易日期')[factor].rank(ascending=factors_rank_dict[factor], method='first')
        # 将计算好的因子rank添加到list中
        merge_factor_list.append(factor + '_rank')

    # 对量价因子进行等权合并，生成新的因子
    df['因子'] = df[merge_factor_list].mean(axis=1)
    # 对因子进行排名
    df['排名'] = df.groupby('交易日期')['因子'].rank(method='first')

    # 选取排名靠前的股票
    df = df[df['排名'] <= select_stock_num]

    return df
# !!!
