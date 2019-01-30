# this is for testing for common values 
# package
library(foreign)
library(stargazer)
library(ggplot2)
library(cramer)
# can not install
# library(RVAideMemoire)
# load sample 
# set the location first
sample= read.csv(file="sample_raw1_df.csv", header=TRUE, sep="\t",encoding = "UTF-8")


# clean the data.
sample_c = data_clean(sample)

# control for city the results sucks
# sample_c=sample_c[sample_c['city']=='chengdu',]

# start the CVM test
for (i in seq(2, 6, by=2)){
  sp1= sample_c[sample_c$num_bidder==i,'win_norm']
  sp2= sample_c[sample_c$num_bidder==(i+1),'win_norm']
  
  print(cramer.test(sp1,sp2))
  
}

# plot the ecdf 

sp1= sample_c[sample_c$num_bidder==2,'win_norm']
sp2= sample_c[sample_c$num_bidder==4,'win_norm']
sp3= sample_c[sample_c$num_bidder==6,'win_norm']

df <- data.frame(x = c(sp1,sp2,sp3), ggg=factor(rep(1:3, c(length(sp1),length(sp2),length(sp3)))))
ggplot(df, aes(x, colour = ggg)) + 
  stat_ecdf()+
  scale_colour_hue(name="", labels=c('N=2','N=4', 'N=6')) + 
  ylab("ecdf") +
  xlab("winning price / reserve price")

# All reject under pooled case


# functions for data cleaning
data_clean=function(data){
  data=data[data[,'priority_people']==0,]
  data[,'win_norm']=data[,'win_bid'] / data[,'reserve_price'] 
  data=data[complete.cases(data[ , 'win_norm']),]
  tall=quantile(data$win_norm, c(0.95),na.rm= TRUE)
  data=data[data['win_norm']<tall,]
  return(data)
}