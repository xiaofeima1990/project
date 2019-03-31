# this script is used for analyzing the priority people 
# and the relation with price , number of bidders 
# I try to find asymmetric information evidence here
library(foreign)
library(stargazer)
library(plm)
# try to use sample1_df
sample= read.csv(file=file.path("E:/github/Project/economics/auction/test", "sample1_df.csv"), header=TRUE, sep="\t",encoding = "UTF-8")
View(sample)


sample2=data_clean(sample,'bid_freq',sample$bid_freq,0.01)
sample2=data_clean(sample,'win_bid',sample$win_bid,0.01)
sample2=data_clean(sample2,'reserve_price',sample$reserve_price,0.01)
sample2=data_clean(sample2,'resev_proxy',sample$resev_proxy,0.05)
# --------------------------------------------------------------------------------
# summary statistics
# --------------------------------------------------------------------------------

sample20=sample2[sample2$priority_people==0,]
sample20['ladder_ratio']=sample20['bid_ladder']/sample20['reserve_price']
sample20['reserve_1000']=sample20['reserve_price']/1000
summary(sample20)
stargazer(sample20)


sample21=sample2[sample2$priority_people==1,]
sample20['ladder_ratio']=sample20['bid_ladder']/sample20['reserve_price']
sample20['reserve_1000']=sample20['reserve_price']/1000
summary(sample20)
stargazer(sample20)



# ---------------------------------------------------------------------------------
# first time auction regression
# ---------------------------------------------------------------------------------

# regress on price index without control on city and year
reg_pri0 = lm(resev_proxy ~ p_res_eva + num_bidder+priority_people , data = sample2)
summary(reg_pri0)
# regress on number of bidders without control city and year
reg_pri_bidder0 = lm(num_bidder ~ p_res_eva +priority_people , data = sample2)
summary(reg_pri_bidder0)

# regress on price index with control on city and year
reg_pri_bidder1 = lm(num_bidder ~ p_res_eva +priority_people +factor(city)+factor(year), data = sample2)
summary(reg_pri_bidder1)

# regress on number of bidders with control on city and year
reg_pri1 <- lm(resev_proxy ~ p_res_eva+num_bidder+priority_people+factor(city)+factor(year) , data=sample2)
summary(reg_pri1)


# regress on bidding spread without control on city and year
reg_pri_bid0 <- lm(dist_high ~ p_res_eva+num_bidder+priority_people, data=sample2)
summary(reg_pri_bid0)


# regress on bidding spread with control on city and year
reg_pri_bid1 <- lm(dist_high ~ p_res_eva+num_bidder+priority_people+factor(city)+factor(year) , data=sample2)
summary(reg_pri_bid1)

# regress on bidding freq without control on city and year
reg_pri_freq0 <- lm(bid_freq ~ p_res_eva+num_bidder+priority_people, data=sample2)
summary(reg_pri_freq0)


# regress on bidding freq with control on city and year
reg_pri_freq1 <- lm(bid_freq ~ p_res_eva+num_bidder+priority_people+factor(city)+factor(year), data=sample2)
summary(reg_pri_freq1)


# output the results for resev_proxy
stargazer(reg_pri0,reg_pri1,reg_pri_bidder0,reg_pri_bidder1,type='text')
stargazer(reg_pri1,reg_pri_bidder1,reg_pri_freq1, type='text')


# ---------------------------------------------------------------------------------
# second time auction regression
# ---------------------------------------------------------------------------------
sample3= read.csv(file=file.path("E:\\Dropbox\\academic\\ideas\\IO field\\justice auction\\code2\\analysis\\", "sample2_df.csv"), header=TRUE, sep="\t",encoding = "UTF-8")
View(sample)
sample4=data_clean(sample3,'resev_proxy',sample$resev_proxy,0.01)


# regress on price index without control on city and year
reg_pri0 = lm(resev_proxy ~ p_res_eva + num_bidder+priority_people , data = sample4)
summary(reg_pri0)
# regress on number of bidders without control city and year
reg_pri_bidder0 = lm(num_bidder ~ p_res_eva +priority_people , data = sample4)
summary(reg_pri_bidder0)

# regress on price index with control on city and year
reg_pri_bidder1 = lm(num_bidder ~ p_res_eva +priority_people +factor(city)+factor(year), data = sample4)
summary(reg_pri_bidder1)

# regress on number of bidders with control on city and year
reg_pri1 <- lm(resev_proxy ~ p_res_eva+num_bidder+priority_people+factor(city)+factor(year) , data=sample4)
summary(reg_pri1)


# output the results for resev_proxy
stargazer(reg_pri0,reg_pri1,reg_pri_bidder0,reg_pri_bidder1,type='latex')







# -----------------------------------------------------
# function part 
# -----------------------------------------------------

data_clean=function(data,name,col,num){
  #  col[which(is.nan(col))] = NA
  #  col[which(col==Inf)] = NA
  #   data=na.omit(col)
  #   quantile(col, c(.05, .5, .95)) 
  #data=data[!(is.na(col)),]
  tall=quantile(col, c(1.0-num),na.rm= TRUE)
  bottom=quantile(col, c(num),na.rm= TRUE)
  data=data[data[name]<tall,]
  data=data[data[name]>bottom,]
  
  return(data)
}