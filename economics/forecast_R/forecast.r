library(BMR)
library(xlsx)
library(xts)
library(lmtest)

rawdata=read.xlsx("rawdatabvar.xlsx",1)

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
  
  result=list(mse=rmse,predict=one_step_ahead)
  return (result)
}
	
get_data <- function(var_list,indep){
    data_list <- list()
	for ( i in var_list){
	 data_list[[length(data_list)+1]] <- indep[,i]
	}
	data_list <- data.frame(data_list)
	return(data_list)
}

remove_selected <- function(var_list,indep){

}


generate_combination <- function(dep,indep,n){
message("preparing combination run down list for cluster computing")


return (rundown_list)
}

model_select <- function(rundown_list,prior) {
message ("starting model selection with cluster computing, this could take a while...")

message("model selection finished, best RMSE is...")
message(best_rmse)
return (best_model)
}


rawdata <- read.xlsx("rawdatabvar.xlsx",1)
tsdata=xts(rawdata[,-1],as.Date(rawdata$NA.,format = "%Y-%m"))
dependent = tsdata[,9]
independent = tsdata[,-9]
independent =cbind(independent,lag(independent))
independent =cbind(independent,diff(independent))

test_fun= function(x){
  print(x)
}