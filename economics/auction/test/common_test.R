# this is for testing for common values 
# main testing reference 
# https://stats.stackexchange.com/questions/288416/non-parametric-test-if-two-samples-are-drawn-from-the-same-distribution
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


# vectorize the distribution function
ori_cdf_v=Vectorize(ori_cdf)


# clean the data.
sample_c = data_clean(sample)

# control for city the results sucks
# sample_c=sample_c[sample_c['city']=='suzhou',]
# control for location specific, we can still reject under number = 2 or 3


# start the CVM test
for (i in seq(2, 6, by=2)){
  sp1= sample_c[sample_c$num_bidder==i,'win_norm']
  sp2= sample_c[sample_c$num_bidder==(i+1),'win_norm']
  e_sp1=ecdf(sp1)
  e_dist_i1=ori_cdf_v(e_sp1(sp1),i)
  e_sp2=ecdf(sp2)
  e_dist_i2=ori_cdf_v(e_sp2(sp2),i+1)
  
  # normalize to the same support to make comparison
  df_sp1=data.frame(sp1,e_dist_i1)
  names(df_sp1) = c("x",'ecdf')
  
  df_sp2=data.frame(sp2,e_dist_i2)
  names(df_sp2) = c("x",'ecdf')
  
  lower_bound=max(min(df_sp1$x),min(df_sp2$x))
  upper_bound=min(max(df_sp1$x),max(df_sp2$x))
  df_sp1=df_sp1[df_sp1$x<upper_bound,]
  df_sp1=df_sp1[df_sp1$x>lower_bound,]
  
  df_sp2=df_sp2[df_sp2$x<upper_bound,]
  df_sp2=df_sp2[df_sp2$x>lower_bound,]  
  
  print("----------------------------------")
  print(cramer.test(df_sp1$ecdf,df_sp2$ecdf))
  print(ks.test(df_sp1$ecdf,df_sp2$ecdf))
  print("----------------------------------")
}

# plot the ecdf 

sp1= sample_c[sample_c$num_bidder==4,'win_norm']
sp2= sample_c[sample_c$num_bidder==5,'win_norm']
sp3= sample_c[sample_c$num_bidder==6,'win_norm']


e_dist_1 = ori_cdf_v(ecdf(sp1)(sp1),4)
e_dist_2 = ori_cdf_v(ecdf(sp2)(sp2),5)
e_dist_3 = ori_cdf_v(ecdf(sp3)(sp3),6)

df <- data.frame(x = c(e_dist_1,e_dist_2,e_dist_3), ggg=factor(rep(1:3, c(length(e_dist_1),length(e_dist_2),length(e_dist_3)))))
ggplot(df, aes(x, colour = ggg)) + 
  stat_ecdf()+
  scale_colour_hue(name="", labels=c('N=4','N=5', 'N=6')) + 
  ylab("ecdf") +
  xlab("quantile of winning price / reserve price")+
  ggtitle("ECDF Across Different Number of Bidders")





# functions for data cleaning
data_clean=function(data){
  data=data[data[,'priority_people']==0,]
  data[,'win_norm']=data[,'win_bid'] / data[,'reserve_price'] 
  data=data[complete.cases(data[ , 'win_norm']),]
  tall=quantile(data$win_norm, c(0.95),na.rm= TRUE)
  data=data[data['win_norm']<tall,]
  return(data)
}

# function to calculate the parentral distribution
parent_F=function(x,ecdf,n) n*x^(n-1)-(n-1)*x^n -ecdf


ori_cdf = function (ecdf,n){
  parent_cdf=uniroot(parent_F,c(0, 1), tol = 0.0001, ecdf = ecdf,n=n)$root
  return(parent_cdf)
}

ori_cdf_v=Vectorize(ori_cdf)
e_dist_3=ori_cdf_v(e_sp1(sp1),i)

