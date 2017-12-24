import plotly as py
import plotly.graph_objs as go
from plotly import tools
import os
import pandas as pd
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class Plot():

    def __init__(self, stockData, recorder, portfolios):
        self.stockData = stockData
        self.recorder = recorder
        self.portfolios = portfolios
        self.plotQueue = {}

        self.rowNum = 2

    def __plot_html(self, fig, filePath, stockNum):

        logger.debug("Save File:" + filePath + "/dashboard.html")
        py.offline.plot(fig, filename = (filePath + "/dashboard.html"), auto_open=False)
        #py.offline.plot(fig, filename = (filePath + "/dashboard.html"))
        pass

    def __genOhlcData(self, dataframe, startDate=None, endDate=None):
        df = dataframe.loc[startDate:endDate]

        trace = go.Ohlc(x=df.index,
            name = "K Line",
            open=df.OpenPrice,
            high=df.MaxPrice,
            low=df.MinPrice,
            close=df.ClosePrice,
            increasing=dict(line=dict(color= '#FF0000')),
            decreasing=dict(line=dict(color= '#008000')))

        return trace

    def __genScatterData(self, dataframe, colName, lineName=None, color='#17BECF', startDate=None, endDate=None):
        if lineName==None:
            lineName = colName

        df = dataframe.loc[startDate:endDate]

        trace = go.Scatter(
            x=df.index,
            y=df[colName],
            name = lineName,
            line = dict(color=color),
            opacity = 0.8)

        return trace

    def __genDotData(self, dataframe, colName, lineName=None, color='#17BECF', startDate=None, endDate=None):
        if lineName==None:
            lineName = colName

        df = dataframe.loc[startDate:endDate]

        trace = go.Scatter(
            x=df.index,
            y=df[colName],
            mode='markers',
            name = lineName,
            line = dict(color=color),
            opacity = 0.8)

        return trace

    def __genBarData(self, dataframe, colName, lineName=None, color='#17BECF', startDate=None, endDate=None, allDate=False):
        if lineName==None:
            lineName = colName

        
        if allDate==False:
            series = dataframe[colName].loc[startDate:endDate]
        else:
            startDate_dt = datetime.strptime(startDate, "%Y-%m-%d")
            endDate_dt = datetime.strptime(endDate, "%Y-%m-%d")
            index = pd.date_range(startDate_dt, endDate_dt, freq='D').strftime("%Y-%m-%d")

            series = pd.Series(index=index)

            series = series.fillna(0)

            series = dataframe[colName].append(series)      #make sure the      
            series = series[~series.index.duplicated(keep='first')]     #drop duplicated index
            series = series.sort_index()

        trace = go.Bar(
            x=series.index,
            y=series,
            name = lineName,
            marker=dict(
                color=color),
            opacity = 0.8)

        return trace

    def addPlot2Queue(self, stockNum, dataframe, colName, colNum=1, rowNum=None, lineName=None, color='#17BECF', startDate=None, endDate=None):
        if rowNum==None:
            rowNum = self.rowNum

        if stockNum not in self.plotQueue:
            self.plotQueue[stockNum] = []

        self.plotQueue[stockNum].append(dict(rowNum=rowNum,
                                dataframe=dataframe,
                                colNum=colNum,
                                colName=colName,
                                lineName=lineName,
                                color=color,
                                startDate=startDate,
                                endDate=endDate))

    def __findMaxMin(self, dataframe, colName, startDate=None, endDate=None):

        dataframe = dataframe[colName].loc[startDate:endDate]
        maxData = dataframe.max().max()
        minData = dataframe.min().min()

        return maxData, minData

    def __plotDataInQueue(self, stockNum, fig):
        maxData=[]
        minData=[]

        for queue in self.plotQueue[stockNum]:
            temp = self.__findMaxMin(queue["dataframe"], [queue["colName"]])

            maxData.append(temp[0])
            minData.append(temp[1])

            data = self.__genScatterData(queue["dataframe"],
                                            queue["colName"],
                                            queue["lineName"],
                                            queue["color"],
                                            queue["startDate"],
                                            queue["endDate"])
            fig.append_trace(data, queue["rowNum"], queue["colNum"])

        self.plotQueue[stockNum] = []

        return [max(maxData), min(minData)]

    def saveResult(self, path):
        for stockNum in self.stockData:
            filePath = path + "/" + stockNum

            if not os.path.exists(filePath):
                os.makedirs(filePath)


            #add plot here
            self.__plot_dashboard(filePath, stockNum)

    def __plot_dashboard(self, filePath, stockNum):
        #++
        #need to modify this function in later version
        logger.info("plot dashboard")
        """
        layout:

        ----------------row1 (performance)----------------
            yaxis1:		revenue line
            yaxis3:		buy vol bar
            yaxis4:		sell vol bar
            yaxis5:		bearishBuy vol bar
            yaxis6:		bearishSell vol bar
            yaxis7:		total vol line

        ----------------row2 (stock status)---------------
            yaxis2:		candle line + ta line
            yaxis8:		vol bar

        """


        rowNum = self.rowNum
        layoutRatio_row1_up = 2
        layoutRatio_row1_low = 3 # up!=low, bcz some over lap is ok
        layoutRatio_row2_up = 5
        layoutRatio_row2_low = 4 # up!=low, bcz some over lap is ok

        stockData = self.stockData[stockNum].data
        record = self.recorder.data[stockNum]
        tradeHistory = self.portfolios.data[stockNum].tradeHistory



        fig = self.__initFig_oneCol(rowNum, stockNum + " Dashboard")
        fig['layout']['yaxis1']['domain'] =[0.7, 1.0]
        fig['layout']['yaxis2']['domain'] =[0.0, 0.65]
        # performance row, plot 1 (revenue line)
        maxVal = minVal = []
        
        #	revenue line
        performance_MarketValLine = self.__genScatterData(record,
                                                            "Market Value",
                                                            color="#1E90FF")#blue
        temp = self.__findMaxMin(record, ["Market Value"])
        fig.append_trace(performance_MarketValLine, 1, 1)
        #	calibrate layout
        maxVal, minVal = self.__findMaxMin(record, ["Market Value"])
        fig['layout']['yaxis1'].update(range= [minVal-(maxVal-minVal)/layoutRatio_row1_up, maxVal]) # 2/3

        # performance row, plot 3 (buy vol bar)
        maxVal = minVal = []

        performance_buyVolBar = self.__genBarData(tradeHistory["buy"],
                                                    "Volume",
                                                    allDate=True,
                                                    startDate=self.stockData[stockNum].testingDateRegion.min,
                                                    endDate=self.stockData[stockNum].testingDateRegion.max,
                                                    lineName="Vol-buy",
                                                    color="#FF0000")#red          
          
        temp = self.__findMaxMin(tradeHistory["buy"], ["Volume"])
        maxVal.append(temp[0])
        minVal.append(temp[1])
        fig.append_trace(performance_buyVolBar, 1, 1)

        # performance row, plot 4 (sell vol bar)
        performance_sellVolBar = self.__genBarData(-pd.DataFrame(tradeHistory["sell"]["Volume"]),
                                                    "Volume",
                                                    allDate=True,
                                                    startDate=self.stockData[stockNum].testingDateRegion.min,
                                                    endDate=self.stockData[stockNum].testingDateRegion.max,
                                                    lineName="Vol-sell",
                                                    color="#008000")#red
        temp = self.__findMaxMin(tradeHistory["sell"], ["Volume"])
        maxVal.append(temp[0])
        minVal.append(temp[1])
        fig.append_trace(performance_sellVolBar, 1, 1)

        # performance row, plot 5 (bearishBuy vol bar)
        performance_bearishBuyVolBar = self.__genBarData(tradeHistory["bearishBuy"],
                                                            "Volume",
                                                            allDate=True,
                                                            startDate=self.stockData[stockNum].testingDateRegion.min,
                                                            endDate=self.stockData[stockNum].testingDateRegion.max,
                                                            lineName="Vol-bearishBuy",
                                                            color="#ffff00")#red
        temp = self.__findMaxMin(tradeHistory["bearishBuy"], ["Volume"])
        maxVal.append(temp[0])
        minVal.append(temp[1])
        fig.append_trace(performance_bearishBuyVolBar, 1, 1)

        # performance row, plot 6 (bearishSell vol bar)
        performance_bearishSellVolBar = self.__genBarData(-pd.DataFrame(tradeHistory["bearishSell"]["Volume"]),
                                                            "Volume",
                                                            allDate=True,
                                                            startDate=self.stockData[stockNum].testingDateRegion.min,
                                                            endDate=self.stockData[stockNum].testingDateRegion.max,
                                                            lineName="Vol-bearishSell",
                                                            color="#800080")#red
        temp = self.__findMaxMin(tradeHistory["sell"], ["Volume"])
        maxVal.append(temp[0])
        minVal.append(temp[1])
        fig.append_trace(performance_bearishSellVolBar, 1, 1)

        #	calibrate layout plot 2+3+4+5 (bar buy + sell)
        maxVal = abs(max(maxVal))
        minVal = 0

        
        fig['layout']['yaxis3'].update(range= [0, maxVal+(maxVal-minVal)*layoutRatio_row1_low]) # 2/3
        fig['layout']['yaxis4'].update(range= [0, maxVal+(maxVal-minVal)*layoutRatio_row1_low]) # 2/3
        fig['layout']['yaxis5'].update(range= [0, maxVal+(maxVal-minVal)*layoutRatio_row1_low]) # 2/3
        fig['layout']['yaxis6'].update(range= [0, maxVal+(maxVal-minVal)*layoutRatio_row1_low]) # 2/3

        # performance row, plot 7 (total vol line)
        maxVal = minVal = []
        performance_totalVolLine = self.__genScatterData(record, "Total Volume", lineName="Vol-in hand")
        maxVal, minVal = self.__findMaxMin(record, ["Total Volume"])
        fig.append_trace(performance_totalVolLine, 1, 1)

        #	calibrate layout plot 7 (total vol line)
        fig['layout']['yaxis7'].update(range= [minVal-(maxVal-minVal)/layoutRatio_row1_up, maxVal]) # 2/3


        # stock status row, plot 8 (vol bar)
        maxVal = minVal = []
        #   vol bar
        volBar = self.__genBarData(stockData, "Vol", color="#1E90FF")#blue
        maxVal, minVal = self.__findMaxMin(stockData, ["Vol"])
        fig.append_trace(volBar, rowNum, 1)
        #   calibrate layout
        fig['layout']['yaxis'+str(8)].update(range= [minVal, maxVal+(maxVal-minVal)*layoutRatio_row2_low])

        # stock status row, plot 2 (candle line + ta line)
        maxVal = minVal = []

        #	candle line
        statistics_kLine = self.__genOhlcData(stockData)
        temp = self.__findMaxMin(stockData, ["OpenPrice","MaxPrice","MinPrice","ClosePrice"])
        maxVal.append(temp[0])
        minVal.append(temp[1])
        fig.append_trace(statistics_kLine, rowNum, 1)
        #	ta line
        if stockNum in self.plotQueue:
            taLineNum = len(self.plotQueue[stockNum])
            temp = self.__plotDataInQueue(stockNum, fig) #for custom ta line
            maxVal.append(temp[0])
            minVal.append(temp[1])
            #	calibrate layout
            maxVal = max(maxVal)
            minVal = min(minVal)
            fig['layout']['yaxis2'].update(range= [minVal-(maxVal-minVal)/layoutRatio_row2_up, maxVal]) # 2/3
        else:
            taLineNum = 0

        
        #update data-yaxis mapping
        #++
        #temp use here
        fig['data'][1].update(yaxis='y'+str(3))
        fig['data'][2].update(yaxis='y'+str(4))
        fig['data'][3].update(yaxis='y'+str(5))
        fig['data'][4].update(yaxis='y'+str(6))
        fig['data'][5].update(yaxis='y'+str(7))
        fig['data'][6].update(yaxis='y'+str(8))
        fig['data'][7].update(yaxis='y'+str(2))

        #   ta line
        for idx in range(8,8+taLineNum):
            fig['data'][idx].update(yaxis='y'+str(2))


        del fig["layout"]['yaxis1']['anchor']
        del fig["layout"]['yaxis1']['position']
        #pprint.pprint(fig["layout"])

        """
        layout:

        ----------------row1 (performance)----------------
            yaxis1:		revenue line
            yaxis3:		buy vol bar
            yaxis4:		sell vol bar
            yaxis5:		bearishBuy vol bar
            yaxis6:		bearishSell vol bar
            yaxis7:		total vol line

        ----------------row2 (stock status)---------------
            yaxis2:		candle line + ta line
            yaxis8:		vol bar

        """

        #fig['data'][-1].update(yaxis='y'+str(rowNum+1))


        self.__plot_html(fig, filePath, stockNum)


    def __mergeRow(self, layout, rowNum, mergeRowCnt, realRowCnt):


        yaxis = dict(overlaying='y'+str(realRowCnt),
                        side='right',
                        showgrid= False,
                        showticklabels=False)

        if rowNum==realRowCnt:
            yaxis.update(anchor='x1')



        layout['yaxis'+str(rowNum+mergeRowCnt)] = yaxis

        return (mergeRowCnt+1), layout

    def __initFig_oneCol(self, rowNum, title):

        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=3,
                     label='3m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                     label='1y',
                     step='year',
                     stepmode='backward'),
                dict(step='all')
            ])
        )

        rangeslider=dict(thickness=0.05)


        # init layout
        fig = tools.make_subplots(rows=rowNum, cols=1,
            shared_xaxes=True,
            shared_yaxes=True,
            vertical_spacing=0.05,
            print_grid=False)

        # add button
        fig["layout"]["xaxis1"]["rangeselector"]=rangeselector
        fig["layout"]["xaxis1"]["rangeslider"]=rangeslider

        # set x index to date
        fig["layout"]["xaxis1"]["type"]='date'

        # title
        fig['layout'].update(title=title)

        # merge row
        realRowCnt=1
        mergeRowCnt=1
        # 	row 1 merge
        #		yaxis2
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)
        #		yaxis3
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)
        #		yaxis4
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)
        #		yaxis5
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)
        #		yaxis6
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)

        realRowCnt+=1
        # 	row 2 merge
        #		yaxis8
        mergeRowCnt, fig["layout"] = self.__mergeRow(fig["layout"], rowNum, mergeRowCnt, realRowCnt)

        return fig

