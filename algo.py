from typing import Dict, List
import numpy as np
import pandas as pd
from datamodel import OrderDepth, TradingState, Order, Trade
import math

ban_data = []
coc_data = []
pina_data = []
div_data = []
picnic_data = []

picnic_dict = {}

def dolph_dive_indicators(df):
    df["yesterday"] = df["sightings"].shift(1) 
    df["diff"] = abs(df["sightings"] - df["yesterday"])
    df["atr"] = df["diff"].rolling(50).mean().shift()
    df["dolph_300ma"] = df["sightings"].rolling(300).mean()
    df["Long"] = np.where(df["diff"] > 50*df["atr"], 1, 0)
    df["Short"] = np.where(df["diff"] < -50*df["atr"], 1, 0)
    df["Long_Exit"] = np.where(df["sightings"] < df.dolph_300ma, 1, 0)
    df["Short_Exit"] = np.where(df["sightings"] > df.dolph_300ma, 1, 0)

def arb_indicators(df):
    df["total"] = 2*df["BAGUETTE"] + 4*df["DIP"] + df["UKULELE"]
    df["ratio"] = df["PICNIC_BASKET"]/df["total"]
    df["50_MA"] = df["ratio"].rolling(50).mean()
    df["50_std"] = df["ratio"].rolling(50).std()
    df["21_MA"] = df["ratio"].rolling(21).mean()
    df["z_score"] = (df["21_MA"] - df["50_MA"])/df["50_std"]
    df["Long"] = np.where(df["z_score"] < -1, 1, 0)
    df["Short"] = np.where(df["z_score"] > 1, 1, 0)

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                if product not in state.market_trades:
                    state.market_trades[product] = [0]

                trades: Trade = state.market_trades[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Following Pablo's banana trades, need to manage trade size to keep up
                for trade in trades:
                    if trade.buyer == "Pablo" and len(order_depth.sell_orders) > 0:
                        # Buy
                        print("BUY", str(math.ceil(trade.quantity/30)) + "x", trade.price)
                        orders.append(Order(product, trade.price, math.ceil(trade.quantity/30)))

                    if trade.seller == "Pablo" and len(order_depth.buy_orders) > 0:
                        # Buy
                        print("SELL", str(math.ceil(trade.quantity/30)) + "x", trade.price)
                        orders.append(Order(product, trade.price, -math.ceil(trade.quantity/30)))
                    
                result[product] = orders

            if product == 'COCONUTS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                if product not in state.market_trades:
                    state.market_trades[product] = [0]
                    
                trades: Trade = state.market_trades[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                
                # Following Charlie for Coconut and Pina Coladas trades, need to also manage trade size. Using math.ceil to round up
                for trade in trades:
                    if trade.buyer == "Charlie" and len(order_depth.sell_orders) > 0:
                        # Buy
                        print("BUY", str(math.ceil(trade.quantity/8)) + "x", trade.price)
                        orders.append(Order(product, trade.price, math.ceil(trade.quantity/8)))

                    if trade.seller == "Charlie" and len(order_depth.buy_orders) > 0:
                        # Buy
                        print("SELL", str(math.ceil(trade.quantity/8)) + "x", trade.price)
                        orders.append(Order(product, trade.price, -math.ceil(trade.quantity/8)))
                    
                result[product] = orders

            if product == 'PINA_COLADAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                if product not in state.market_trades:
                    state.market_trades[product] = [0]
                    
                trades: Trade = state.market_trades[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                for trade in trades:
                    if trade.buyer == "Charlie" and len(order_depth.sell_orders) > 0:
                        # Buy
                        print("BUY", str(math.ceil(trade.quantity/4)) + "x", trade.price)
                        orders.append(Order(product, trade.price, math.ceil(trade.quantity/4)))

                    if trade.seller == "Charlie" and len(order_depth.buy_orders) > 0:
                        # Buy
                        print("SELL", str(math.ceil(trade.quantity/4)) + "x", trade.price)
                        orders.append(Order(product, trade.price, -math.ceil(trade.quantity/4)))
                    
                result[product] = orders

            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:

                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above

            if product == "BERRIES":

                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []
                
                time = state.timestamp

                if 100000 < time < 300000: # Morning Period
                    if (time-100000)%3 == 0:
                        if len(order_depth.sell_orders) > 0:
                            # Load up on berries
                            best_ask = min(order_depth.sell_orders.keys())
                            best_ask_volume = order_depth.sell_orders[best_ask]
                            print("BUY", str(6) + "x", best_ask)
                            orders.append(Order(product, best_ask, 1))
                
                elif 440000 < time < 560000: # Peak Hours
                    if len(order_depth.buy_orders) > 0:
                        # Sell berries
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]
                        print("SELL", str(-1) + "x", best_bid)
                        orders.append(Order(product, best_bid, -1))

                result[product] = orders
            
            if product == "DIVING_GEAR":
                # Catch the peak difference between Diving Gear and Dolphin sightings, using 50*average true range (atr)
                # as indicator for long/short points, exit point is when doplhin sightings exceeds or goes below 300 day average
                # (300 day used because we want to hold longer and not sell straight away)

                orders: list(Order) = []
                order_depth: OrderDepth = state.order_depths[product]

                if product not in state.position:
                    state.position[product] = 0

                div_col = {"timestamp": state.timestamp, "Product": product, "bid": 0, "ask": 0, 
                           "sightings": state.observations["DOLPHIN_SIGHTINGS"]}
                div_col["bid"] = max(order_depth.buy_orders)
                div_col["ask"] = min(order_depth.sell_orders)
                div_col["mid_price"] = (div_col["bid"] + div_col["ask"])/2

                div_data.append(pd.DataFrame(div_col, index=[0]))
                div = pd.concat(div_data).reset_index(drop=True)

                if len(div) > 50:
                    dolph_dive_indicators(div)
                    if div.iloc[len(div)-1].Long:
                        if len(order_depth.sell_orders) > 0:
                            best_ask = min(order_depth.sell_orders.keys())
                            best_ask_volume = order_depth.sell_orders[best_ask]
                            print("BUY", str(50) + "x", best_ask)
                            orders.append(Order(product, best_ask, 50))

                    if div.iloc[len(div)-1].Long_Exit:
                        if state.position[product] > 0 and len(order_depth.buy_orders) > 0:
                            best_bid = max(order_depth.buy_orders.keys())
                            print("SELL", str(state.position[product]) + "x", best_bid)
                            orders.append(Order(product, best_bid, -state.position[product]))

                    if div.iloc[len(div)-1].Short:
                        if len(order_depth.buy_orders) > 0:
                            best_bid = max(order_depth.buy_orders.keys())
                            print("SELL", str(50) + "x", best_bid)
                            orders.append(Order(product, best_bid, -50))
                    
                    if div.iloc[len(div)-1].Short_Exit:
                        if state.position[product] < 0 and len(order_depth.sell_orders) > 0:
                            best_ask = max(order_depth.sell_orders.keys())
                            print("BUY", str(-state.position[product]) + "x", best_ask)
                            orders.append(Order(product, best_ask, -state.position[product]))
                
                result[product] = orders
        
            if product == "BAGUETTE":
                if product not in state.position:
                    state.position[product] = 0
                order_depth: OrderDepth = state.order_depths[product]
                picnic_dict[product] = (max(order_depth.buy_orders) + min(order_depth.sell_orders))/2
            
            if product == "DIP":
                if product not in state.position:
                    state.position[product] = 0
                order_depth: OrderDepth = state.order_depths[product]
                picnic_dict[product] = (max(order_depth.buy_orders) + min(order_depth.sell_orders))/2
            
            if product == "UKULELE":
                if product not in state.position:
                    state.position[product] = 0
                order_depth: OrderDepth = state.order_depths[product]

                picnic_dict[product] = (max(order_depth.buy_orders) + min(order_depth.sell_orders))/2

            if product == "PICNIC_BASKET":
                if product not in state.position:
                    state.position[product] = 0
                order_depth: OrderDepth = state.order_depths[product]

                picnic_dict[product] = (max(order_depth.buy_orders) + min(order_depth.sell_orders))/2

        
        picnic_dict["diff"] = picnic_dict["PICNIC_BASKET"] - (2*picnic_dict["BAGUETTE"] + 4*picnic_dict["DIP"] + picnic_dict["UKULELE"])
        
        bag_depth: OrderDepth = state.order_depths["BAGUETTE"]
        bag_orders: list(Order) = []

        dip_depth: OrderDepth = state.order_depths["DIP"]
        dip_orders: list(Order) = []

        uku_depth: OrderDepth = state.order_depths["UKULELE"]
        uku_orders: list(Order) = []

        pic_depth: OrderDepth = state.order_depths["PICNIC_BASKET"]
        pic_orders: list(Order) = []

        # Arbitraging picnic basket and all their components, important to make sure of net zero position.

        if picnic_dict["diff"] > 550:
            # Long Total, Short Basket
            # Buy Baguette
            if len(bag_depth.sell_orders) > 0:
                best_ask = min(bag_depth.sell_orders.keys())

                if state.position["BAGUETTE"] <= -140:
                    print("BUY", str(state.position["BAGUETTE"]) + "x", best_ask)
                    bag_orders.append(Order("BAGUETTE", best_ask, state.position["BAGUETTE"]))
                
                else:
                    print("BUY", str(10) + "x", best_ask)
                    bag_orders.append(Order("BAGUETTE", best_ask, 10))
                
                result["BAGUETTE"] = bag_orders

            # Buy Dip
            if len(dip_depth.sell_orders) > 0:
                best_ask = min(dip_depth.sell_orders.keys())

                if state.position["DIP"] <= -280:
                    print("BUY", str(state.position["DIP"]) + "x", best_ask)
                    dip_orders.append(Order("DIP", best_ask, state.position["DIP"]))
                
                else:
                    print("BUY", str(20) + "x", best_ask)
                    dip_orders.append(Order("DIP", best_ask, 20))
                
                result["DIP"] = dip_orders

            # Buy Ukulele
            if len(uku_depth.sell_orders) > 0:
                best_ask = min(uku_depth.sell_orders.keys())

                if state.position["UKULELE"] <= -70:
                    print("BUY", str(state.position["UKULELE"]) + "x", best_ask)
                    uku_orders.append(Order("UKULELE", best_ask, state.position["UKULELE"]))
                
                else:
                    print("BUY", str(5) + "x", best_ask)
                    uku_orders.append(Order("UKULELE", best_ask, 5))
                
                result["UKULELE"] = uku_orders
            
            # Short Picnic
            if len(pic_depth.buy_orders) > 0:
                best_bid = max(pic_depth.buy_orders.keys())

                if state.position["PICNIC_BASKET"] >= 70:
                    print("SELL", str(state.position["PICNIC_BASKET"]) + "x", best_bid)
                    pic_orders.append(Order("PICNIC_BASKET", best_bid, -state.position["PICNIC_BASKET"]))

                else:
                    print("SELL", str(5) + "x", best_bid)
                    pic_orders.append(Order("PICNIC_BASKET", best_bid, -5))

                result["PICNIC_BASKET"] = pic_orders

        if picnic_dict["diff"] < 250:
            # Long Basket, Short Total

            if len(bag_depth.buy_orders) > 0:
                best_bid = max(bag_depth.buy_orders.keys())

                if state.position["BAGUETTE"] >= 140:
                    print("SELL", str(state.position["BAGUETTE"]) + "x", best_bid)
                    bag_orders.append(Order("BAGUETTE", best_bid, -state.position["BAGUETTE"]))
                
                else:
                    print("SELL", str(10) + "x", best_bid)
                    bag_orders.append(Order("BAGUETTE", best_bid, -10))
                
                result["BAGUETTE"] = bag_orders

            # Sell Dip
            if len(dip_depth.buy_orders) > 0:
                best_bid = max(dip_depth.buy_orders.keys())

                if state.position["DIP"] >= 280:
                    print("SELL", str(state.position["DIP"]) + "x", best_bid)
                    dip_orders.append(Order("DIP", best_bid, -state.position["DIP"]))
                
                else:
                    print("SELL", str(20) + "x", best_bid)
                    dip_orders.append(Order("DIP", best_bid, -20))
                
                result["DIP"] = dip_orders

            # Sell Ukulele
            if len(uku_depth.buy_orders) > 0:
                best_bid = max(uku_depth.buy_orders.keys())

                if state.position["UKULELE"] >= 70:
                    print("SELL", str(state.position["UKULELE"]) + "x", best_bid)
                    uku_orders.append(Order("UKULELE", best_bid, -state.position["UKULELE"]))
                
                else:
                    print("SELL", str(5) + "x", best_bid)
                    uku_orders.append(Order("UKULELE", best_bid, -5))
                
                result["UKULELE"] = uku_orders
            
            # Buy Picnic
            if len(pic_depth.sell_orders) > 0:
                best_ask = min(pic_depth.sell_orders.keys())

                if state.position["PICNIC_BASKET"] <= -70:
                    print("BUY", str(state.position["PICNIC_BASKET"]) + "x", best_ask)
                    pic_orders.append(Order("PICNIC_BASKET", best_ask, state.position["PICNIC_BASKET"]))

                else:
                    print("BUY", str(5) + "x", best_ask)
                    pic_orders.append(Order("PICNIC_BASKET", best_ask, 5))
                
                result["PICNIC_BASKET"] = pic_orders
            
        return result