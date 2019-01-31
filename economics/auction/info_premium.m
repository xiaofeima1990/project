% test for the info premium
% this test aims at verifying the argument in the Dionne et al 2009
% that equilibrium price premium is indepdendent of number of bidders
% To testfiy this, we have to derive the coeffients under two different 
% scenario.  




% construct the SIGMA
sig_v=1;
sig_a=0.8;
sig_e=0.4;



%% uninformed, symmetric case
% we care about the second highest bidder's bidding outcome

for N = 3:6 
% sigma
SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
% covaraince i 
COVi= sig_v * ones(N,1);
COVi(2) = COVi(2) + sig_a;
coeff1=inv(SIGMA) * COVi;
X = ['coeffient under N =', num2str(N),' is :',num2str(coeff1') ];
disp(X)
XX = ['The sum is :',num2str(sum(coeff1))];
disp(XX)
end


%% informed case 
% in this case informed bidder is the one who wins the auction
% construct the SIGMA

for N = 3:6 
% sigma
SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
% first order is the informed guy
SIGMA(1,1)=sig_v+sig_a;
% covaraince i=2 
COVi= sig_v * ones(N,1);
COVi(2) = COVi(2) + sig_a;
coeff1=inv(SIGMA) * COVi;
X = ['coeffient under N =', num2str(N),' is :',num2str(coeff1') ];
disp(X)
% we have to adjust the denominator, because we have to derive the expected
% private signal for the informed bidder given i=2 
% after adjustment, the sum of the coefficient is identical to the 
% uninformed case. 
XX = ['The sum is :',num2str((sum(coeff1) - coeff1(1))/(1 - coeff1(1)))];
disp(XX)
end

%% pure IPV situation
sig_v=1;
sig_a=0.8;
sig_e=0.4;


coeff = sig_v / (sig_v + sig_a + sig_e)


%% eigen decposition 

% symmetric case 
N=3;
SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
[V,D] = eig(SIGMA)