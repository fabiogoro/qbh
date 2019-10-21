#include "qbh.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int ALPHA = 1;
int BETA = 2;
float GAMMA = 1.0;
float DELTA = 0.3;
float ZETA = 0.15;
float ETA = 1.0;
int DIMENSION = 1;

void update(int max, int maxstart, double* best, int j, int N){
  float delta = DELTA*N;
  int maxl = j-maxstart+2;
  int bestl = best[2]-best[1]+1;
  if ((max>best[0]&&maxl>delta)||(max==best[0]&&bestl>maxl)){
    best[0] = max;
    best[1] = maxstart;
    best[2] = j;
  }
}

void propagation(int i, int j, int* Acur, int* Aprev, int* Bcur, int* Bprev, int* cur, int* prev, int N){
  int alpha = ALPHA-1;
  int beta = BETA;

  if (i-Bcur[i-1]<=beta && j-Aprev[i]<=alpha){
    if (cur[i-1]>=prev[i]){
      cur[i] = cur[i-1];
      cur[i+N+1] = cur[i-1+N+1];
      Acur[i] = Acur[i-1];
      Bcur[i] = Bcur[i-1];
    } else {
      cur[i] = prev[i];
      cur[i+N+1] = prev[i+N+1];
      Acur[i] = Aprev[i];
      Bcur[i] = Bprev[i];
    }    
  } else if (j-Aprev[i]<=alpha){
    cur[i] = prev[i];
    cur[i+N+1] = prev[i+N+1];
    Acur[i] = Aprev[i];
    Bcur[i] = Bprev[i];
  } else if (i-Bcur[i-1]<=beta){
    cur[i] = cur[i-1];
    cur[i+N+1] = cur[i-1+N+1];
    Acur[i] = Acur[i-1];
    Bcur[i] = Bcur[i-1];
  } else {
    cur[i] = 0;
    cur[i+N+1] = 0;
    Acur[i] = 0;
    Bcur[i] = 0;
  }
}

// TODO allow different dimensions.
int compare(double *q, int i, double *x, int j, int N, int M){
  if(DIMENSION==1){
    float eps = ceil(ZETA*fabs(q[i]));
    return !(x[j]<q[i]-eps || x[j]>q[i]+eps);
  }
  else if(DIMENSION==2){
    float eps = ceil(ZETA*fabs(q[i]));
    float epsN = ceil(ZETA*fabs(q[i+N]));
    return !(x[j]<q[i]-eps || x[j]>q[i]+eps || 
        x[j+M]<q[i+N]-epsN || x[j+M]>q[i+N]+epsN);
  } else return 0; // Dimension other than 1 and 2 have 0 score.
  //int ans = 1;
//printf("%f\t%f\n",q[i+N],x[j+M]);
  //if(x[j]>=0){
  //  if(x[j]/(1+eps)>q[i]) ans=0;
  //  else if(x[j]*(1+eps)<q[i]) ans=0;
  //}else{
  //  if(x[j]/(1+eps)<q[i]) ans=0;
  //  else if(x[j]*(1+eps)>q[i]) ans=0;
  //}

  //if(x[j]<q[j]-eps || x[j]>q[j]+eps || 
  //return ans && (
  //    x[j+M]>2*ETA*q[i+N+1] || x[j+M]-q[i+N+1]<-2*ETA) 
  //  ans=0;
}

void reset(int j,int* cur,int* prev,int* Acur,int* Aprev,int* Bcur,int* Bprev,int N, int M, double* q, double* x){
  int beta = BETA;
  int i;
  float r = (int)(GAMMA*N);
  for(i=1; i<N+1; i++)
    if(j-cur[i+N+1]+2==r){
      if(compare(q,i-1,x,j,N,M)) {
        cur[i] = 1;
        cur[i+N+1] = j+1;
        Acur[i] = j+1;
        Bcur[i] = i;
      } else {
        if(j-prev[i+N+1]+1<r-1){
          propagation(i,j,Acur,Aprev,Bcur,Bprev,cur,prev,N);
        } else if (i-Bcur[i-1]<=beta){
          cur[i] = cur[i-1];
          cur[i+N+1] = cur[i-1+N+1];
          Acur[i] = Acur[i-1];
          Bcur[i] = Bcur[i-1];
        } else {
          cur[i] = 0;
          cur[i+N+1] = 0;
          Acur[i] = 0;
          Bcur[i] = 0;
        }
      }
    }
}

double smbgt(double *q, double *x, int N, int M, int alpha, int beta, double gamma, double delta, double zeta, double eta, int dimension, int debug){
  ALPHA = alpha;
  BETA = beta;
  GAMMA = gamma;
  DELTA = delta;
  ZETA = zeta;
  ETA = eta;
  DIMENSION = dimension;
  int i, j;
  double best[3] = {0,0,0};
  int max=0, maxstart=0;

  int cur[(N+1)*2];
  int prev[(N+1)*2];
  int Aprev[N+1];
  int Bprev[N+1];
  for (j = 0; j < N+1; j++) {
    prev[j] = 0;
    prev[j+N+1] = 1;
    Aprev[j] = -ALPHA-2;
    Bprev[j] = -BETA-2;
  }

  int Acur[N+1];
  int Bcur[N+1];

  for (i = 0; i < M; i++) {
    cur[0] = 0;
    cur[0+N+1] = i+2;
    Bcur[0] = 1;
    for (j = 1; j < N+1; j++) {
      if(compare(q,j-1,x,i,N,M)){
        cur[j] = prev[j-1]+1;
        cur[j+N+1] = prev[j-1+N+1];
        Acur[j] = i+1;
        Bcur[j] = j;
      }
      else{
        cur[j+N+1] = 0;
        propagation(j,i,Acur,Aprev,Bcur,Bprev,cur,prev,N);
      }
    }
    max = 0;
if(debug==1){
if(i==0){
  printf("\t\t");
  for(j=0;j<N;j++)
    printf("(%f %f)",q[j], q[j+N]);
}
printf("\n(%f %f)\t",x[i], x[i+M]);
}
    for (j = 0; j < N+1; j++)
      if (cur[j]>max) {
        max = cur[j];
        maxstart = cur[j+N+1];
      }
    update(max,maxstart,best,i,N);
    reset(i,cur,prev,Acur,Aprev,Bcur,Bprev,N,M,q,x);


    for (j = 0; j < N+1; j++) {
if(debug==1)
printf("%d ",cur[j]);
      prev[j] = cur[j];
      prev[j+N+1] = cur[j+N+1];
      Aprev[j] = Acur[j];
      Bprev[j] = Bcur[j];
    }
if(debug==1){
printf("\t");
for (j = 1; j < N+1; j++)
printf("%d ",cur[j+N+1]);
printf("\n\n");
}
  }

  return best[0]/N;
}

double _get_norm(double *u, int size){
  double norm = 0;
  for (int n = 0; n < size; n++) {
    norm += u[n]*u[n];
  }
  norm = sqrt(norm);
  return norm;
}

double dtw(double *q, double *x, int N, int M){
  double *SSM;
  //double q_norm = _get_norm(q, N);
  //double x_norm = _get_norm(x, M);
  //double norm = q_norm*q_norm;
  int n, m, s, i;
  int segment[2] = {0, M};
  int sbbn = 0;
  int sbbm = 0;
  int S = 3;
  int dn[3] = {1, 1, 0};
  int dm[3] = {1, 0, 1};
  int dw[3] = {1, 1, 1};
  double *ED;
  double best = N;
  double actual, score;
  int step_n, step_m, eN, eM;

  //if(x_norm>q_norm) norm = x_norm*x_norm;
  M+=1;
  SSM = (double*) calloc(N*M, sizeof(double));
  /*for (n = 0; n < N; n++) {
    for(m = 0; m < M; m++) {
      //SSM[m*N+n] = 0;
      printf("%d ", m*N+n);
    }
    printf("\n");
  }*/
  //printf("\n");

  for (n = 0; n < N; n++) {
    for(m = 0; m < M-1; m++) {
      SSM[(m+1)*(N)+n] = sqrt(pow(q[n]-x[(m+segment[0])],2));
      //printf("%.1f ", SSM[(m)*(N)+n]);
    }
   // printf("\n");
  }
  //printf("\n");

  for (s = 0; s < S; s++) {
    if(sbbn < dn[s]) sbbn = dn[s];
    if(sbbm < dm[s]) sbbm = dm[s];
  }
  eN = N+sbbn;
  eM = M+sbbm;

  ED = (double*) malloc(eN*eM * sizeof(double));

  for (i = 0; i < eN * eM; i++) {
    ED[i] = 999999;
  }
  ED[(sbbm)*eN+sbbn-1] = 0;


  //accumulate
  for (n = sbbn; n < eN; n++) {
    // special column, m=0
    m = sbbm;
    //if ( ED[m*eN+(n-1)] >= ED[(eM-1)*eN+(n-1)] ) {
      //E[(n-sbbn)+(m-sbbm)*N] = 0;
      ED[(n)+m*eN] = ED[(m)*eN+(n-1)];
    //}
    /*else {*/
      //ED[(n)+(m)*eN] = ED[(eM-1)*eN+(n-1)];
    //}
    // special column, m=1
    m = sbbm+1;
    ED[(n)+(m)*eN] = ED[(n)+(m-1)*eN] + SSM[(n-sbbn)+(m-sbbm)*N];

    //  ordinary DTW with given stepsizes
    for(m = sbbm+1; m < eM; m++) {

      for (s = 0; s < S; s++) {
        step_n = n-dn[s];
        step_m = m-dm[s];
        //printf("step: (%d,%d) ",step_n,step_m);

        if (step_m>sbbm) {
          score = ED[(step_n)+(step_m)*eN]+SSM[(n-sbbn)+(m-sbbm)*N]*dw[s];
          //printf("score: %f",score);

          if (score < ED[(n)+(m)*eN]) {
            ED[(n)+(m)*eN] = score;
          }
        }
      }
      actual = ED[(n)+(m)*eN];
      //printf("%.1f ", actual);
    }
    if(actual<best) best = actual;
    //printf("Best: %.1f", best);
    //printf("\n");
  }

  free(SSM);
  SSM = NULL;
  free(ED);
  ED = NULL;

  return best;
}

