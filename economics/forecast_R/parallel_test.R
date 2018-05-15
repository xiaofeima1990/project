#load library 
library(BMR)
library(xlsx)
library(xts)
library(lmtest)
library(iterpc)
library(foreach)
library(doParallel)
#library(parallel)
load("F:/RD/develop/R/temp.RData")
# read data and clean data 
rawdata <- read.xlsx("rawdatabvar.xlsx",1)
tsdata=xts(rawdata[,-1],as.Date(rawdata$NA.,format = "%Y-%m"))
dependent = tsdata[,9]
independent = tsdata[,-9]
independent =cbind(independent,lag(independent))
independent =cbind(independent,diff(independent))
independent = independent[-1,]
independent = independent[-1,]
dependent   = dependent[-1,]
dependent   = dependent[-1,]


## function setup
pred_r_squared <- function(linear.model) {
  lm.anova <- anova(linear.model)
  tss <- sum(lm.anova$"Sum Sq")
  # predictive R^2
  pred.r.squared <- 1 - PRESS(linear.model)/(tss)
  return(pred.r.squared)
}

PRESS <- function(linear.model) {
  pr <- residuals(linear.model)/(1 - lm.influence(linear.model)$hat)
  PRESS <- sum(pr^2)
  return(PRESS)
}

best_rsq_var <- function(dep,indep){
  var_names <- character()
  rsq_v <- numeric()
  
  for (i in names(indep)){
    lmrsq <- lm(dep ~ indep[,i])
    rsq_pred <- pred_r_squared(lmrsq)
    if (rsq_pred > 0.2) {
      var_names <- append(var_names,i)
      rsq_v <- append(rsq_v,rsq_pred)
    }
  }
  df <- data.frame(var_names,rsq_v)
  df <- df[order(df$rsq_v,decreasing = TRUE),]
  return(df)
}

best_granger_var <- function(dep,indep,lag_peroid){
  var_names <- character()
  granger_P <- numeric()
  for (i in names(indep)){
    grander_var <- grangertest(dep ~ indep[,i],order = lag_peroid)
    prf <- grander_var[2,4]
    if (prf < 0.01) {
      var_names <- append(var_names,i)
      granger_P <- append(granger_P,prf)
    }
  }
  df <- data.frame(var_names,granger_P)
  df <- df[order(df$granger_P),]
  return(df)
}

RMSE_bvar_backtest <- function(bvar_vectors,backtest,prior){
  one_step_ahead <- numeric()
  for (i in 1:backtest){
    model <- BVARM(head(bvar_vectors,-i),prior,p = 12, constant = T, irf.periods = 1,keep = 10000, burnin = 1000, VType =1,HP1=0.5,HP2 = 0.5, HP3 = 10)
    model_forecast <- forecast(model,shocks = FALSE, backdata = 12, save = FALSE,plot = FALSE)
    one_step_ahead[i] <- model_forecast$MeanForecast[1,1]
  }
  error <-tail(bvar_vectors[,1],backtest)-rev(one_step_ahead)
  rmse <- sqrt(mean(error^2))
  return (rmse)
}

## get the candidate variable

rsq_list_name=best_rsq_var(dependent,independent)

list_name=rsq_list_name[,1]
II=iterpc(table(list_name),2)
iter_list=getall(II)

name_1=c("import_yoy","real_est_invsmt_yoy.1")





result_list=list()

parallel_func=function(var_name2,var_name1,dependent,independent,prior_set,backtest){
  ## initialization 
  temp_result=list()
  
  
  ## BVAR function
  ### combine into a data
  name_list=c(var_name2,var_name1)
  
  bvar_vectors=cbind(dependent,independent[,name_list])
  prior=c(prior_set,prior_set,prior_set,prior_set,prior_set,prior_set)
  backtest = 12
  prior_set=0.9
  prior=rep(prior_set,times=5)
  
  temp_rmse=tryCatch({
    RMSE_bvar_backtest(bvar_vectors,backtest,prior)
    },error=function(e){
      ""
    })
  
  
  
  ## saving result
  temp_result[[1]]=temp_rmse
  temp_result[[2]]=bvar_vectors
  temp_result[[3]]=prior_set
  
  
  #result_list[[length(result_list)+1]] <<- temp_result ## assign to gobal variable <<-
  
  return(temp_result)
  
  
  
}

## ----new function for averaging ---##


Average_forecast <- function(model_list,name_1,dependent=dependent,independent=independent,backtest,prior,Weight){
  # model_list is a multi-list
  
  one_step_ahead <- numeric()
  forecast_list=list()
  n_mlist=dim(model_list)[1]
  RRmse=numeric()
  for (j in 1:n_mlist){
    name_list=c(model_list[j,],name_1)
    bvar_vectors=cbind(dependent,independent[,name_list])
    prior=rep(prior,times=(1+2+dim(model_list)[2]))
    for (i in 1:backtest){
      model=tryCatch({BVARM(head(bvar_vectors,-i),prior,p = 12, constant = T, irf.periods = 1,keep = 10000, burnin = 1000, VType =1,HP1=0.5,HP2 = 0.5, HP3 = 10)
                      },error=function(e){
                        ""})
      model_forecast=tryCatch({forecast(model,shocks = FALSE, backdata = 12, save = FALSE,plot = FALSE)
      },error=function(e){
        ""})
      one_step_ahead[i] =tryCatch({model_forecast$MeanForecast[1,1]
      },error=function(e){
        ""})
     
    }
    
    forecast_list[[j]]=one_step_ahead

  }
  
  
  ## model average
  forecast_list=t(matrix(unlist(forecast_list),ncol=n_mlist))
  forecast_list=matrix(as.numeric(forecast_list),nrow=nrow(forecast_list))
  ## basic average 
  A_f_result=apply(forecast_list,2,mean)
  W_f_result=apply(forecast_list,2,function(x){weighted.mean(x,Weight)})
  

  ## calculate MSE
  error <-tail(bvar_vectors[,1],backtest)-rev(A_f_result)
  rmse1 <- sqrt(mean(error^2))
  error <-tail(bvar_vectors[,1],backtest)-rev(W_f_result)
  rmse2 <- sqrt(mean(error^2))
  for (i in 1:dim(forecast_list)[1]){
    error =tail(bvar_vectors[,1],backtest)-rev(forecast_list[i,])
    RRmse[i]=sqrt(mean(error^2))
  }
  result=c(rmse1,rmse2,RRmse)
  result=data.frame(t(result))
  colnames(result)[1]="B_average"
  colnames(result)[2]="W_average"
  return (result)
}





##singel tset
print("start simple test ")
parallel_func(iter_list[2,],var_name1=name_1,dependent=dependent,independent=independent,result_list=result_list)


### test for parallel computing
test_fun= function(x){
  print(x)
}

#print("for parallel computing simple test")
#cl <- makeCluster(2) #set core to compute
#registerDoParallel(cl)
#foreach(x=2:6,.combine='cbind')%dopar%test_fun(x)
#x=foreach(x=2:6,.combine='cbind')%dopar%parallel_func(iter_list[x,],var_name1=name_1,dependent=dependent,independent=independent,result_list=result_list)
#stopCluster(cl)

#x=foreach(x=1:5,.combine='cbind')%dopar%test_fun(x) # combine the result of the foreach 


### test for parallel computing 
print("for parallel computing BVAR test") 
cl <- makeCluster(2)
registerDoParallel(cl)
#foreach(x=iter(iter_list,by='row'))%dopar%test_fun(x)
result_x=foreach(x=1:6,.combine='cbind',.packages='BMR')%dopar%parallel_func(iter_list[x,],var_name1=name_1,dependent=dependent,independent=independent,result_list=result_list)
stopCluster(cl)

## processing the data 
#result_x = data.frame(matrix(unlist(t(result_x)),nrow=6))


## get optimal value
## rmse matrix
t_result=matrix(unlist(t(result_x[1:2,])),ncol =2)
t_result=matrix(as.numeric(t_result),ncol=ncol(t_result))


## name matrix
model_list=t(matrix(unlist(result_x[3,]),nrow =2))

model_list[order(t_result[,1]),]


model_list=model_list[1:5,]

Weight=c(5,4,3,2,1)/15

backtest=3
prior=0.9
Average_forecast(model_list,name_1,dependent=dependent,independent=independent,backtest,prior,Weight)

#savehistory("F:/RD/develop/R/r_log_8_25-2.txt")