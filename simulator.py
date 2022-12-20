import preprocesser as pr
from positions import Positions
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

class Simulater:
    def __init__(self, stocks, starting_bal):
        self.stocks = stocks
        self.starting_bal = starting_bal
        self.cur_bal = starting_bal
        self.portfolio = []
        self.portfolio_val_by_day = []

    def sell_stocks(self, day):
        for index, stock in enumerate(self.portfolio):
            for ticker_d, df in self.stocks.items():
                if day < df.shape[0]:
                    _, ticker_p, _, qty = stock
                    if ticker_p == ticker_d:  
                        price = df.iloc[day]['close']
                        if df.iloc[day]['positions'] == -1:
                            gross_profit = qty * price
                            self.cur_bal += gross_profit
                            self.portfolio.pop(index)
                            print(f'Day {day + 1} sold {qty} units of {ticker_p} at ${price} for a total of ${gross_profit}')
                        else:
                            print(f'Day {day + 1}: no selling activity')
    
    def select_candidate(self, candidates):
        return max(candidates) if candidates else []
            
    def get_optimal_stock_by_price(self, day):
        candidates = []
        for ticker, df in self.stocks.items():
            if day < df.shape[0]:
                position = df.iloc[day]['positions']
                price = df.iloc[day]['close']

                if position == 1:
                    num_shares = self.cur_bal // price
                    total_value = price * num_shares
                    if not total_value:
                        continue
                    candidates.append((total_value, ticker, price, num_shares))
        return self.select_candidate(candidates)
    
    def get_portfolio_value_by_day(self):
        max_days = max([df.shape[0] for df in self.stocks.values()])

        for day in range(max_days):
            total_value = 0
            for stock in self.portfolio:
                _, ticker_p, _, qty = stock
                for ticker_d, df in self.stocks.items():
                    if day < df.shape[0] and ticker_p == ticker_d:
                        price = df.iloc[day]['close']
                        total_value += price * qty
                        self.portfolio_val_by_day.append(total_value)

    def get_portfolio_value_ending(self):
        for stock in self.portfolio:
            _, ticker_p, _, qty = stock
            for ticker_d, df in self.stocks.items():
                price = df.iloc[-1]['close']
                if ticker_p == ticker_d:
                    total = qty * price
                    # print(f'{ticker_p}: ${total} -> ${price} * {qty}')
                    return total
    
    def run_simulation(self):
        max_days = max([df.shape[0] for df in self.stocks.values()])
        
        for day in range(max_days):
            # sell phase
            self.sell_stocks(day)

            # buy phase
            optimal_stock = self.get_optimal_stock_by_price(day)
            if not optimal_stock:
                print(f'Day {day + 1}: no buying activity')
                continue

            total_cost, ticker, price, qty = optimal_stock

            if self.cur_bal < total_cost:
                print(f'Day {day+1}: Not enough balance to buy {ticker}')
            else:
                self.cur_bal -= total_cost
                self.portfolio.append(optimal_stock)
                print(f'Day {day + 1} bought {qty} units of {ticker} at ${price} for a total of ${total_cost}')

        return self.cur_bal

    def display_trends(self):
        colors = []

        for i in range(len(self.portfolio_val_by_day) - 1):
            if self.portfolio_val_by_day[i + 1] > self.portfolio_val_by_day[i]:
                colors.append('green')
            else:
                colors.append('red')


        for i in range(len(self.portfolio_val_by_day) - 1):
            plt.plot([i, i+1], [self.portfolio_val_by_day[i], self.portfolio_val_by_day[i+1]], color=colors[i])   

        plt.xlabel('Day')
        plt.ylabel('Total Value of Portfolio')
        plt.title('Total Value of Portfolio over Time')
        plt.subplots_adjust(left=0.20)

        plt.show()

def main():
    df_grouped = pr.read_and_group_stock()
    pr.process_group(df_grouped)

    sim = Simulater(Positions._positions, 100000)

    print(f'Starting balance: ${sim.cur_bal:.2f}')
    final_balance = sim.run_simulation()
    print(f'Final balance: ${final_balance:.2f}')

    sim.get_portfolio_value_by_day()
    for index, value in enumerate(sim.portfolio_val_by_day):
        print(f'Day {index + 1}: ${value:.2f}')

    sim.display_trends()

if __name__ == '__main__':
    main()