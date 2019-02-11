% optimal reserve price 

%% the parameter set
comm_mu = 0.07;
beta    = 0.955;
epsilon_mu = 0;
comm_var = 0.025;
priv_var = 0.005;
epsilon_var = 0.036;

reserve=0.8;

MU    = comm_mu + log(reserve)*beta;
SIGMA = comm_var + priv_var + epsilon_var;

% running the simple case
implict_fu = @(r) r - (1-cdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA))/pdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA);

r_est = fsolve(implict_fu,0.5);
r_est

%% lower bound 
comm_mu = 0.05242;
beta    = 0.79;
epsilon_mu = 0;
comm_var = 0.02196;
priv_var = 0.00165;
epsilon_var = 0.028;

SIGMA = comm_var + priv_var + epsilon_var;

% running the simple case
implict_fu = @(r) r - (1-cdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA))/pdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA);

r_est = fsolve(implict_fu,0.5);
r_est

%% upper bound 
comm_mu = 0.07;
beta    = 0.8;
epsilon_mu = 0;
comm_var = 0.03196;
priv_var = 0.01;
epsilon_var = 0.0935;

SIGMA = comm_var + priv_var + epsilon_var;

% running the simple case
implict_fu = @(r) r - (1-cdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA))/pdf('Lognormal',r,comm_mu+log(r)*beta,SIGMA);

r_est = fsolve(implict_fu,0.5);
r_est

