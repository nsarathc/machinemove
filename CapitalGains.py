from collections import deque
from datetime import date
from prettytable import PrettyTable

import copy
import pdb
import csv
import pprint
import types


class Defaults(object):
    UNIT_PRECISION = 4
    AMOUNT_PRECISION = 2
    PURCHASE = ('Purchase', 'Systematic Investment', 'Lateral Shift In')
    REDEEM = ('Redemption', 'Lateral Shift Out', 'Systematic Withdrawal', 'S T P Out')
    DAYS3YEARS = 3*365


class transactionRecord(object):
    def __init__(self, txnDate, txnNav, txnAmount, txnUnits):        
        self.txnDate = txnDate        
        self.txnAmount = round(float(txnAmount), Defaults.AMOUNT_PRECISION)
        self.txnNav = txnNav
        if txnUnits is None: 
            self.txnUnits = round(txnAmount/float(txnNav), Defaults.UNIT_PRECISION)
        else:
            self.txnUnits = round(txnUnits, Defaults.UNIT_PRECISION)

    def sortKey(self):
        return self.txnDate
            
    def __repr__(self):
        return "%s %s %s %s" % \
            (self.txnDate, self.txnNav, self.txnAmount, self.txnUnits)
        
        
class purchaseTransaction(transactionRecord):
    def __init__(self, txnDate, txnNav, txnAmount, txnUnits):
        super(purchaseTransaction, self).__init__(
                            txnDate, txnNav, txnAmount, txnUnits)
        self.txnType = "Purchase"

    def __repr__(self):
        return "%s %s" % (self.txnType, super(purchaseTransaction, self).__repr__())


class sellTransaction(transactionRecord):
    def __init__(self, txnDate, txnNav, txnAmount, txnUnits):
        super(sellTransaction, self).__init__(
                            txnDate, txnNav, txnAmount, txnUnits)
        self.txnType = "Redemption"

    def __repr__(self):
        return "%s %s" % (self.txnType, super(sellTransaction, self).__repr__())


class redemptionBucket(object):
    def __init__(self):
        self.redemptionTransaction = None
        self.purchaseTransactions = []

    def __repr__(self):
        return "%s \n\t  %s" % (self.redemptionTransaction, self.purchaseTransactions)

    def addRedemptionTransaction(self, sellTransaction):
        self.redemptionTransaction = sellTransaction

    def addMatchedPurchaseTransaction(self, purchaseTransaction):
        pt = copy.deepcopy(purchaseTransaction)
        pt.txnAmount = round(pt.txnUnits * pt.txnNav, Defaults.AMOUNT_PRECISION)
        self.purchaseTransactions.append(pt)

    def printHardformatted(self):
        x = PrettyTable()
        
        x.field_names = ['Sale']
        x.add_row([str("%.4f" % self.redemptionTransaction.txnUnits)  \
                   + ' units on ' + str(self.redemptionTransaction.txnDate) \
                   + ' at NAV of ' + str("%.4f" % self.redemptionTransaction.txnNav) \
                   + ' : ' \
                   ])

        y = PrettyTable()
        y.field_names = ['Buy Date', 'Buy NAV', 'Units', 'Days Held', 'Gain', 'Type']

        print "*~"*36 + "*"
        for rec in self.purchaseTransactions:
            daysHeld = (self.redemptionTransaction.txnDate - rec.txnDate).days
            if daysHeld > Defaults.DAYS3YEARS:
                holdingTerm = 'Long Term'
            else:
                holdingTerm = 'Short Term'
            y.add_row([rec.txnDate, \
                       rec.txnNav, \
                       rec.txnUnits, \
                       daysHeld, \
                       round((self.redemptionTransaction.txnNav - rec.txnNav) * rec.txnUnits, Defaults.AMOUNT_PRECISION), \
                       holdingTerm])

        print x
        print y
        print "\n"
                  
        
def generateRedemptionBuckets(sellTxnRecList, purchaseTxnRecList):    
    sellQ = sorted(sellTxnRecList, key=sellTransaction.sortKey)
    buyQ = deque(sorted(purchaseTxnRecList, key=purchaseTransaction.sortKey))

    redemptionBucketList = []
    
    for saleRec in sellQ:
        redemBucket = redemptionBucket()
        redemBucket.addRedemptionTransaction(saleRec)
        buyRec = buyQ.popleft()

        if saleRec.txnUnits == buyRec.txnUnits:
            redemBucket.addMatchedPurchaseTransaction(buyRec)            
        elif saleRec.txnUnits < buyRec.txnUnits:
            buyRecCopy = copy.deepcopy(buyRec)            
            buyRecCopy.txnUnits = round(saleRec.txnUnits, Defaults.UNIT_PRECISION)
            redemBucket.addMatchedPurchaseTransaction(buyRecCopy)
            buyRec.txnUnits -= saleRec.txnUnits
            buyRec.txnUnits = round(buyRec.txnUnits, Defaults.UNIT_PRECISION)                                    
            buyQ.appendleft(buyRec)
        elif saleRec.txnUnits > buyRec.txnUnits:
            redeemed = 0
            while True:
                buyRec.txnUnits = round(buyRec.txnUnits, Defaults.UNIT_PRECISION)
                redemBucket.addMatchedPurchaseTransaction(buyRec)                
                redeemed += buyRec.txnUnits
                toRedeem = saleRec.txnUnits - redeemed
                buyRec = buyQ.popleft()
                redeemAble = buyRec.txnUnits
                if toRedeem <= redeemAble:
                    buyRecCopy = copy.deepcopy(buyRec)
                    buyRecCopy.txnUnits = round(toRedeem, Defaults.UNIT_PRECISION)
                    redemBucket.addMatchedPurchaseTransaction(buyRecCopy)
                    buyRec.txnUnits -= toRedeem
                    if buyRec.txnUnits <> 0:
                        buyRec.txnUnits = round(buyRec.txnUnits, Defaults.UNIT_PRECISION)                                                
                        buyQ.appendleft(buyRec)
                    break
                else:
                    pass                      
        redemptionBucketList.append(redemBucket)
      
    return redemptionBucketList, buyQ

def toDate(txnDateStr):
    temp = txnDateStr.split('/')
    return date(int(temp[2]), int(temp[1]), int(temp[0]))

def constructBuySellLists(in_csv):
    purchaseList = []
    sellList = []
    
    with open(in_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            txnDate = toDate(row['txnDate'])
            txnNav = float(row['txnNav'])
            txnAmount = float(row['txnAmount'])
            txnUnits = float(row['txnUnits'])
            txnType = row['txnType']
            if txnType in Defaults.PURCHASE:
                p = purchaseTransaction(txnDate, txnNav, txnAmount, txnUnits)
                purchaseList.append(p)
            elif txnType in Defaults.REDEEM:
                s = sellTransaction(txnDate, txnNav, txnAmount, txnUnits)
                sellList.append(s)

    return sellList, purchaseList            
            
            
def runIt():
    sellList, purchaseList = constructBuySellLists('stmt.csv')
    
    results, unredeemed = generateRedemptionBuckets(sellList, purchaseList)

    for result in results:
        result.printHardformatted()
    
    pprint.pprint(unredeemed)
  
if __name__=='__main__':
    runIt()
