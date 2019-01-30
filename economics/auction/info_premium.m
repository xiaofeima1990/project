% test for the info premium
% assume bidder i is in the first order
% assume the informed bidder is in the second order


% construct the SIGMA
sig_v=1;
sig_a=0.8;
sig_e=0.4;

N=3;

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;

COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff1=inv(SIGMA) * COVi;

N=4;

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;

COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff2=inv(SIGMA) * COVi;

gross_leaning=sum(coeff2(2:end))-sum(coeff1(2:end))

N=5; 

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;

COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff3=inv(SIGMA) * COVi;

gross_leaning=sum(coeff3(2:end))-sum(coeff2(2:end))

N=6; 

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;

COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff4=inv(SIGMA) * COVi;

gross_leaning=sum(coeff4(2:end))-sum(coeff3(2:end))




%% informed part 
% construct the SIGMA
sig_v=1;
sig_a=0.8;
sig_e=0.4;

N=3;

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
SIGMA(2,2)=sig_v+sig_a;

COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff1=inv(SIGMA) * COVi;

N=4;

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
SIGMA(2,2)=sig_v+sig_a;
COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff2=inv(SIGMA) * COVi;

gross_leaning=sum(coeff2(2:end))-sum(coeff1(2:end))


N=5; 

SIGMA= diag((sig_a+sig_e)*ones(1,N))+ones(N,N)*sig_v;
SIGMA(2,2)=sig_v+sig_a;
COVi= sig_v * ones(N,1);
COVi(1) = COVi(1) + sig_a;

coeff3=inv(SIGMA) * COVi;

gross_leaning=sum(coeff3(2:end))-sum(coeff2(2:end))
