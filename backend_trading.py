from typing import List, Set, Dict, Optional, Union, Tuple


class Transaction:
    def __init__(self, buyer_id: str, seller_id: str, amount: int, price: int):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.price = price


class Order:
    def __init__(self, trader_id: str, amount: int, price: int):
        self.trader_id = trader_id
        self.amount = amount
        self.price = price


class Stock:
    def __init__(self) -> None:
        self.history: List[Transaction] = []
        self.buyers: List[Order] = []
        self.sellers: List[Order] = []


StockExchange = Dict[str, Stock]


def add_new_stock(stock_exchange: StockExchange, ticker_symbol: str) -> bool:
    if not (ticker_symbol in stock_exchange):
        stock_exchange[ticker_symbol] = Stock()
        return True
    return False


def append_history(stock: Stock, trader_id: str, trader: Order,
                   deal_amount: int, price: int, buyer: bool) -> None:
    if buyer:
        stock.history.append(
            Transaction(trader_id, trader.trader_id, deal_amount,
                        max(trader.price, price)))
    else:
        stock.history.append(
            Transaction(trader.trader_id, trader_id, deal_amount,
                        max(trader.price, price)))


def initialize_amounts(amount: int, trader: Order) -> Tuple[int, int, int]:
    deal_amount = min(amount, trader.amount)
    trader.amount -= deal_amount
    amount -= deal_amount
    return deal_amount, trader.amount, amount


def make_trade(stock: Stock, traders: List[Order], trader_id: str, amount: int,
               price: int, buyer: bool) -> int:
    for trader in reversed(traders):
        if buyer and trader.price > price or \
                not buyer and trader.price < price:
            break
        deal_amount, trader.amount, amount = initialize_amounts(amount, trader)
        append_history(stock, trader_id, trader, deal_amount, price, buyer)
        if trader.amount == 0:
            traders.pop()
        if amount == 0:
            break

    return amount


def classify(traders: List[Order], trader: Order,
             amount: int, buyer: bool) -> None:
    if amount > 0:
        for i in range(len(traders)):
            if buyer and trader.price <= traders[i].price or \
                    not buyer and trader.price >= traders[i].price:
                traders.insert(i, trader)
                return
        traders.append(trader)


def place_buy_sell_order(stock_exchange: StockExchange, ticker_symbol: str,
                         trader_id: str, amount: int, price: int,
                         buyer: bool) -> None:
    stock = stock_exchange[ticker_symbol]
    sellers = stock.sellers
    buyers = stock.buyers

    if buyer:
        amount = make_trade(stock, sellers, trader_id, amount, price, buyer)
        classify(buyers, Order(trader_id, amount, price), amount, buyer)
    else:
        amount = make_trade(stock, buyers, trader_id, amount, price, buyer)
        classify(sellers, Order(trader_id, amount, price), amount, buyer)


def place_buy_order(stock_exchange: StockExchange, ticker_symbol: str,
                    trader_id: str, amount: int, price: int) -> None:
    place_buy_sell_order(stock_exchange, ticker_symbol,
                         trader_id, amount, price, buyer=True)


def place_sell_order(stock_exchange: StockExchange, ticker_symbol: str,
                     trader_id: str, amount: int, price: int) -> None:
    place_buy_sell_order(stock_exchange, ticker_symbol,
                         trader_id, amount, price, buyer=False)


def check_transactions(owned: Dict[str, int], ticker_symbol: str,
                       trade: Transaction, trader_id: str, sec_trade_id: str,
                       buyer: bool) -> None:
    if sec_trade_id == trader_id:
        if ticker_symbol not in owned:
            owned[ticker_symbol] = 0
        if buyer:
            owned[ticker_symbol] += trade.amount
        else:
            owned[ticker_symbol] -= trade.amount


def stock_owned(stock_exchange: StockExchange, trader_id: str) \
        -> Dict[str, int]:
    owned: Dict[str, int] = {}
    for ticker_symbol in stock_exchange:
        stock = stock_exchange[ticker_symbol]
        for trade in stock.history:
            check_transactions(owned, ticker_symbol, trade, trader_id,
                               trade.buyer_id, buyer=True)
            check_transactions(owned, ticker_symbol, trade, trader_id,
                               trade.seller_id, buyer=False)

    return {key: value for key, value in owned.items() if value != 0}


def add_trader(trader_id: str, all_t: Set[str]) -> None:
    if trader_id not in all_t:
        all_t.add(trader_id)


def add_traders(all_t: Set[str], traders: Union[List[Order],
                                                List[Transaction]],
                history: bool) -> None:
    if isinstance(traders, Stock) and history:
        traders = traders.history
    for trader in traders:
        if isinstance(trader, Transaction) and history:
            add_trader(trader.buyer_id, all_t)
            add_trader(trader.seller_id, all_t)
        elif isinstance(trader, Order):
            add_trader(trader.trader_id, all_t)


def all_traders(stock_exchange: StockExchange) -> Set[str]:
    all_t: Set[str] = set()
    for ticker_symbol in stock_exchange:
        stock = stock_exchange[ticker_symbol]
        add_traders(all_t, stock.buyers, history=False)
        add_traders(all_t, stock.sellers, history=False)
        add_traders(all_t, stock.history, history=True)

    return all_t


def transactions_by_amount(stock_exchange: StockExchange,
                           ticker_symbol: str) -> List[Transaction]:
    stock = stock_exchange[ticker_symbol]
    return sorted(stock.history, key=lambda x: x.amount, reverse=True)


def p_s_command_check(command: str, amount: str, ticker: str, at: str,
                      price: str, stock_exchange: StockExchange,
                      trader_id: str) -> bool:
    return command in ("SELL", "BUY") and \
           amount.isdigit() and \
           price.isdigit() and \
           len(ticker) > 0 and \
           ticker in stock_exchange and \
           at == "AT" and \
           len(trader_id) > 0


def add_command_check(command: str, ticker: str) -> bool:
    return command == "ADD" and len(ticker) > 0


def format_command(command: str) -> Union[List[str], bool]:
    colon_index = command.find(":")
    if colon_index == -1:
        return False
    if len(command[colon_index + 2:].split(" ")) != 5:
        return False
    trader_id = command[:colon_index]
    command, amount, ticker, at, price = command[colon_index + 2:].split(" ")

    return [trader_id, command, amount, ticker, at, price]


def pass_sell_or_buy(command: str, stock_exchange: StockExchange) -> bool:
    commands = format_command(command)
    if not isinstance(commands, List):
        return False
    trader_id, command, amount, ticker, at, price = commands
    if not p_s_command_check(command, amount, ticker, at, price,
                             stock_exchange, trader_id):
        return False

    if command == "BUY":
        place_buy_order(stock_exchange, ticker, trader_id,
                        int(amount), int(price))
    elif command == "SELL":
        place_sell_order(stock_exchange, ticker, trader_id,
                         int(amount), int(price))
    return True


def process_batch_commands(stock_exchange: StockExchange,
                           commands: List[str]) -> Optional[int]:
    for i in range(len(commands)):
        if (("SELL" in commands[i]) or ("BUY" in commands[i])) \
                and pass_sell_or_buy(commands[i], stock_exchange):
            continue

        if len(commands[i].split(" ")) != 2:
            return i
        command, ticker = commands[i].split(" ")
        if add_command_check(command, ticker) and \
                add_new_stock(stock_exchange, ticker):
            continue
        return i

    return None
