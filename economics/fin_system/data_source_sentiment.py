# -*- coding: utf-8 -*-
'''
Created on Mon Feb 29 17:08:52 2016

@author: guoxuan
股票情绪分析2
利用通联数据平台 https://app.wmcloud.com/open/mydata?lang=zh
获取新闻 情绪等相关信息
fied 输入返回值的name即可

通联数据凭证

相关资料：
tushare文档 http://tushare.org/
通联数据api 文档 （全）https://api.wmcloud.com/docs/  https://api.wmcloud.com/docs/pages/viewpage.action?pageId=1867793

'''

import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

fd=ts.Subject()


'''
获取新闻关联的证券(含新闻情感)
NewsByTickers

新闻热度指数
NewsHeatIndex

新闻情感指数
NewsSentimentIndex

'''
fd=ts.Subject()
news_senti=fd.NewsByTickers(ticker='300418',
                            beginDate='20160101',endDate='20160229',
                            field='ticker,secShortName,newsID,newsTitle,relatedScore,sentiment,sentimentScore')

news_heated_stock=fd.NewsHeatIndex(ticker='300418',
                                   beginDate='20160101',endDate='20160229',
                                   field='ticker,secShortName,newsPublishDate,heatIndex')

news_senti_stock=fd.NewsSentimentIndex(ticker='300418',
                                   beginDate='20160101',endDate='20160229',
                                   field='ticker,secShortName,newsPublishDate,sentimentIndex')


'''
热点主题部分

主题基本信息
ThemesContent

主题关联的证券
TickersByThemes

获取一段时间内主题新增的关联证券
ThemesTickersInsert

证券关联的主题
ThemesByTickers

主题热度
ThemesHeat
'''
fd=ts.Subject()
# themes
theme_info=fd.ThemesContent(field='themeID,themeName,themeDescription,themeBaseDate,isActive')

# themes related securities
theme_ticker=fd.TickersByThemes(themeID='1,2,3,4',beginDate='20160101',endDate='20160229',
                                field='themeID,themeName,ticker,secShortName,beginDate,isNew,returnScore,textContributionScore,industryScore')
#new added theme's securities
theme_new_ticker=fd.ThemesTickersInsert(themeID='1,2,3,4',beginDate='20160101',endDate='20160229',
                                        field='themeID,themeName,ticker,secShortName,beginDate,isNew,returnScore,textContributionScore,industryScore')
# the heat of the themes
theme_heat=fd.ThemesHeat(themeID='1,2,3,4',beginDate='20160101',endDate='20160229',
                         field='themeID,statisticsDate,themeName,newsNum,newsNumPercent')                                
                                
           
# securities related themes
fd=ts.Subject()
ticker_theme=fd.ThemesByTickers(ticker='300418',
                                field='ticker,beginDate,endDate,themeID,themeName,returnScore,textContributionScore,industryScore')

'''
雪球信息 雪球的权限不够 无法使用，我靠
靠股吧数据

'''
fd=ts.Subject()
XQ_stock=fd.SocialDataXQ(ticker='300418',
                beginDate='20160101',endDate='20160229',
                field='ticker,statisticsDate,postNum,postPercent')
                
Guba_stock=fd.SocialDataGuba(ticker='300418',
                beginDate='20160101',endDate='20160229',
                field='ticker,statisticsDate,postNum,postPercent') 
                
Guba_theme=fd.SocialThemeDataGuba(themeID='1,2,3,4',
                                  beginDate='20160101',endDate='20160229',
                                  field='ticker,statisticsDate,postNum,postPercent') 