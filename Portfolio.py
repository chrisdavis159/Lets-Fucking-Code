"""
Author: Chris Zickert
Title: Portfolio
Description: Takes in a start date and an end date along with any amount of tickers and number of shares for the ticker, and returns different financial data
"""

import pandas_datareader as data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Portfolio:

    def __init__(self, startDate, endDate, stocks):
        #This is the initializer function that will create instances for individualized portfolios. Args startDate and endDate need to be 'YYYY-MM-DD' format.
        
        self.startDate = startDate
        self.endDate = endDate
        self.stocks = stocks
        self.create()
    
    
    def create(self):
        #This method will create the main data frame that I will be able to call into other methods
        
        adjData = {}
        
        for ticker in list(self.stocks.keys()): 
            #Creates dictionary with adjusted close multiplied by number of shares entered for each ticker entered
            wholeDF = data.get_data_yahoo(ticker, self.startDate, self.endDate)
            adjData[ticker] = wholeDF["Adj Close"] * self.stocks[ticker]
            
        #Puts the data in a pd data frame and adds across the collumns for a total portfolio value
        adjDF = pd.DataFrame(data = adjData)
        adjDF["Portfolio Value"] = adjDF.sum(axis = 1)
        adjDF["Portfolio Returns"] = adjDF["Portfolio Value"][1:].values / adjDF["Portfolio Value"][:-1] - 1
        self.adjDF = adjDF
        

    def averageDailyReturn(self):
        #Calculates average daily return of the overall portfolio and returns a float
        
        averageDailyReturn =  ((self.adjDF["Portfolio Returns"].add(1).product()) ** (1 / (len(self.adjDF) - 1))) -1
        return averageDailyReturn


    def volatility(self):
        #Calculates volatility over the lifespan of the portfolio and returns a float

        volatility = np.std(self.adjDF["Portfolio Returns"])
        return volatility
        
        
    def riskRatio(self):
        #Calculates the volatility of the portfolio compared to S&P 500 and returns a float
        
        gspcData = {}
        gspc = data.get_data_yahoo("^GSPC", self.startDate, self.endDate)
        gspcData["^GSPC"] = gspc["Adj Close"]
        gspcDF = pd.DataFrame(data = gspcData)

        riskDF = pd.concat([self.adjDF, gspcDF], axis = 1)
        riskDF["^GSPC Returns"] = riskDF["^GSPC"][1:].values / riskDF["^GSPC"][:-1] - 1

        riskRatio = np.std(self.adjDF["Portfolio Returns"]) / np.std(riskDF["^GSPC Returns"])
        return riskRatio


    def marginalVolatility(self, ticker, shares):
        #Calculates the difference in volatility if a specific ticker with a specific amount of shares is added into the portfolio and returns a float
        
        tickData = {}
        tick = data.get_data_yahoo(ticker, self.startDate, self.endDate)
        tickData[ticker] = tick["Adj Close"] * shares
        tickerDF = pd.DataFrame(data = tickData)

        mvDF = pd.concat([self.adjDF, tickerDF], axis = 1)
        
        mvDF["New Portfolio Value"] = mvDF["Portfolio Value"] + mvDF[ticker]
        mvDF["Stock Returns"] = mvDF["New Portfolio Value"][1:].values / mvDF["New Portfolio Value"][:-1] - 1
     
        marginalVolatility = np.std(mvDF["Stock Returns"]) - np.std(self.adjDF["Portfolio Returns"])  
      
        return marginalVolatility


    def maxDrawDown(self):
        #Calculates the maximum drawdown of your portfolio and returns a float
        Max = self.adjDF["Portfolio Value"].cummax()
        DrawDown = self.adjDF["Portfolio Value"] / Max - 1
        maxDrawDown = DrawDown.cummin()
        return maxDrawDown[-1]


    def totalProfitabilityP(self):
        #Calculated total profitability in the form of a percentage
        totalProfitabilityP = (self.adjDF["Portfolio Value"][-1:].values - self.adjDF["Portfolio Value"][:1].values) / self.adjDF["Portfolio Value"][:1].values
        return totalProfitabilityP


    def totalProfitabilityN(self):
        #Calculates total profitability
        totalProfitabilityN = self.adjDF["Portfolio Value"][-1:].values - self.adjDF["Portfolio Value"][:1].values
        return totalProfitabilityN



    def plotPortfolio(self):
        #Creates and shows a graph of the overall portfolio value
        
        
        
        plt.figure(figsize = (15, 5))
        plt.plot(self.adjDF.index, self.adjDF["Portfolio Value"])
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Portfolio Value")
        plt.show()


portfolio = Portfolio("2010-01-01", "2020-12-31", {"SHOO": 1})
print(portfolio.plotPortfolio())
