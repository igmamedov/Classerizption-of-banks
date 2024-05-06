# Настройки среды
options(scipen = 999)
set.seed(123)                                       

# Подключим дополнительные библиотеки
library("numDeriv")                                      # численное дифференцирование
library("brant")                                         # тест Бранта о parallel lines
library("MASS")                                          # порядковый пробит и логит
library("switchSelection")                               # порядковый пробит и логит
library ("readxl")                                       # чтение эесель файлов
library("car")                                           # для полсчета ViF
  
# Подгружаем данные и приводим категориальные переменные
data = read_excel("C:\\Диплом\\Classerizption-of-banks\\data4regresssion\\final_df.xlsx")
data = as.data.frame(data)
n = nrow(data)

summary(as.factor(data$nps_cluster)) 

#кластеры nps
nps_cluster_0 = rep(0, n) 
nps_cluster_0[data$nps_cluster == 1] = 1
nps_cluster_0 = matrix(nps_cluster_0, ncol = 1)
data$nps_cluster_0 = nps_cluster_0

nps_cluster_1 = rep(0, n) 
nps_cluster_1[data$nps_cluster == 2] = 1 
nps_cluster_1 = matrix(nps_cluster_1, ncol = 1)
data$nps_cluster_1 = nps_cluster_1

nps_cluster_2 = rep(0, n) 
nps_cluster_2[data$nps_cluster == 3] = 1 
nps_cluster_2 = matrix(nps_cluster_2, ncol = 1)
data$nps_cluster_2 = nps_cluster_2

#кластеры financial
fin_cluster_0 = rep(0, n) 
fin_cluster_0[data$fin_cluster == 1] = 1
fin_cluster_0 = matrix(fin_cluster_0, ncol = 1)
data$fin_cluster_0 = fin_cluster_0

fin_cluster_1 = rep(0, n) 
fin_cluster_1[data$fin_cluster == 2] = 1
fin_cluster_1 = matrix(fin_cluster_1, ncol = 1)
data$fin_cluster_1 = fin_cluster_1

fin_cluster_2 = rep(0, n) 
fin_cluster_2[data$fin_cluster == 3] = 1
fin_cluster_2 = matrix(fin_cluster_2, ncol = 1)
data$fin_cluster_2 = fin_cluster_2

fin_cluster_3 = rep(0, n) 
fin_cluster_3[data$fin_cluster == 4] = 1
fin_cluster_3 = matrix(fin_cluster_3, ncol = 1)
data$fin_cluster_3 = fin_cluster_3

fin_cluster_4 = rep(0, n) 
fin_cluster_4[data$fin_cluster == 5] = 1
fin_cluster_4 = matrix(fin_cluster_4, ncol = 1)
data$fin_cluster_4 = fin_cluster_4

fin_cluster_5 = rep(0, n) 
fin_cluster_5[data$fin_cluster == 6] = 1
fin_cluster_5 = matrix(fin_cluster_5, ncol = 1)
data$fin_cluster_5 = fin_cluster_5

#кластеры portfolios
porfolio_cluster_0 = rep(0, n) 
porfolio_cluster_0[data$porfolio_cluster == 0] = 1
porfolio_cluster_0 = matrix(porfolio_cluster_0, ncol = 1)
data$porfolio_cluster_0 = porfolio_cluster_0

porfolio_cluster_1 = rep(0, n) 
porfolio_cluster_1[data$porfolio_cluster == 1] = 1
porfolio_cluster_1 = matrix(porfolio_cluster_1, ncol = 1)
data$porfolio_cluster_1 = porfolio_cluster_1

porfolio_cluster_2 = rep(0, n) 
porfolio_cluster_2[data$porfolio_cluster == 2] = 1
porfolio_cluster_2 = matrix(porfolio_cluster_2, ncol = 1)
data$porfolio_cluster_2 = porfolio_cluster_2

porfolio_cluster_3 = rep(0, n) 
porfolio_cluster_3[data$porfolio_cluster == 3] = 1
porfolio_cluster_3 = matrix(porfolio_cluster_3, ncol = 1)
data$porfolio_cluster_3 = porfolio_cluster_3

porfolio_cluster_4 = rep(0, n) 
porfolio_cluster_4[data$porfolio_cluster == 4] = 1
porfolio_cluster_4 = matrix(porfolio_cluster_4, ncol = 1)
data$porfolio_cluster_4 = porfolio_cluster_4


# Введем пороги (квантили для 0.0, 0.2, 0.4, 0.6, 0.8)
mu <- c(4.03, 40.01, 46.0, 52.09, 60.02)

# Бинаризуем индекст стабильность по порогам
score_labels <- rep(0, n)                           
score_labels[(data$Score > mu[1]) & (data$Score <= mu[2])] <- 0
score_labels[(data$Score > mu[2]) & (data$Score <= mu[3])] <- 1
score_labels[(data$Score > mu[3]) & (data$Score <= mu[4])] <- 2
score_labels[(data$Score > mu[4]) & (data$Score <= mu[5])] <- 3
score_labels[(data$Score > mu[5])] <- 4
score_labels <- matrix(score_labels, ncol = 1)           # приводим к нужному формату
data$score_labels <- score_labels                        # добавим в датафрейм переменную 

summary(as.factor(data$score_labels))                    # посмотрим доли

# Перемешиваем данные
data = data[sample(1:n),]

# Посмотрим на данные
head(data, 5)

#---------------------------------------------------
# Часть 1. Проверка на мультиколлинеарность 
#---------------------------------------------------

# В данных по портфелях и по финансовым показателям 
# есть взаимозаменяемые переменные (потверждается корреляционной матрицой)
# Проводем дополнительный анализ ViF

# все регрессоры
linear_model_0 = lm(Score ~ nps_cluster_1 + nps_cluster_2 +
                            porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                            fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 +
                            Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + ROE +
                            NPL_Ratio + Debt_TotalAssets + Deposits_TotalAssets +
                            TotalLoans_TotalAssets + LDR + LiquidAssetsRatio + Z_score +
                            LoansLE_TotalAssets +
                            AttractedMbcs_TotalAssets + Capital_assets + gos_sobstv + foreign +
                            system + law + strategy + nationhood +
                            news_cluster + A_Shares + A_Promissory_notes +
                            A_bonds + A_capitals + A_corporate_loans + A_individuals_loans +
                            A_loro_loans + A_fixed_assets + A_Mbcs +
                            P_deposits_individuals + P_corporate_funds + P_accounts_individuals +
                            P_bonds_promissory_notes + P_capitals,
                  
                          data=data)
summary(linear_model_0)
summary(linear_model_0)$r.squared

vif_0 = as.matrix(vif(linear_model_0))
write.csv(vif_0, file="vif_before.csv")
# убираем взаимозаменяемые регрессоры
linear_model_1 = lm(Score ~ nps_cluster_1 + nps_cluster_2 +
                            porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                            fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                            law + nationhood + strategy + 
                            Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + 
                            TotalLoans_TotalAssets + Z_score + 
                            gos_sobstv + foreign + system + A_Shares +
                            A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                            P_deposits_individuals + P_corporate_funds + P_capitals,
                        
                    data=data)

summary(linear_model_1)
summary(linear_model_1)$r.squared

vif_1 = as.matrix(vif(linear_model_1))
write.csv(vif_1, file="vif_after.csv")
write.csv(summary(linear_model_1)$coefficients, 'lm_coef.csv')
#---------------------------------------------------
# Часть 2. Оценивание параметров и тест Бранта
#---------------------------------------------------

# Воспользуемся пробит модель, предварительно перекодировав индекс стабильности
data$score_binary <- as.numeric(data$score_labels >= 3)

model_probit <- glm(formula = score_binary ~ nps_cluster_1 + nps_cluster_2 +
                                              porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                                              fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                                              law + securities + strategy + 
                                              Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + Debt_TotalAssets + 
                                              TotalLoans_TotalAssets + Z_score + 
                                              gos_sobstv + foreign + system + A_Shares +
                                              A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                                              P_deposits_individuals + P_corporate_funds + P_capitals,                                              
                    data = data,                                       
                    family = binomial(link = "probit"))             

summary(model_probit) 
write.csv(summary(model_probit) $coefficients, 'probit_coef.csv')

# Проведем тест Бранта для проверки parallel assumption
model_oprobit <- polr(formula = as.factor(score_labels) ~ nps_cluster_1 + nps_cluster_2 +
                                                          porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                                                          fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                                                          law + securities + strategy + 
                                                          Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + 
                                                          TotalLoans_TotalAssets + Z_score + 
                                                          gos_sobstv + foreign + system + A_Shares +
                                                          A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                                                          P_deposits_individuals + P_corporate_funds + P_capitals,                                                 
                      data = data,                                       
                      method = "probit")                                      
summary(model_oprobit) 
brant(model_oprobit)

write.csv(as.matrix(brant(model_oprobit)), 'brant_test.csv')
# Применим порядковую пробит модель
model_orprobit = mvoprobit(score_labels ~ nps_cluster_1 + nps_cluster_2 +
                                          porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                                          fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                                          law + securities + strategy + 
                                          Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + 
                                          TotalLoans_TotalAssets + Z_score + 
                                          gos_sobstv + foreign + system + A_Shares +
                                          A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                                          P_deposits_individuals + P_corporate_funds + P_capitals,
                          data = data)

summary(model_orprobit)
# Применим порядковую логит модель
model_orlogit = mvoprobit(score_labels ~ nps_cluster_1 + nps_cluster_2 +
                                         porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                                         fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                                         law + securities + strategy + 
                                         Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + 
                                         TotalLoans_TotalAssets + Z_score + 
                                         gos_sobstv + foreign + system + A_Shares +
                                         A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                                         P_deposits_individuals + P_corporate_funds + P_capitals,
                          data = data,
                          marginal = list(logistic = NULL))

summary(model_orlogit)
# Оценим порядклвую полупараметрическую модель
model_orsemi = mvoprobit(score_labels ~ nps_cluster_1 + nps_cluster_2 +
                                        porfolio_cluster_1 + porfolio_cluster_2 + porfolio_cluster_3 + porfolio_cluster_4 +
                                        fin_cluster_1 + fin_cluster_2 + fin_cluster_3 + fin_cluster_4 + fin_cluster_5 + 
                                        law + securities + strategy + 
                                        Н1_CAR + Н2_liquidity + Н3_liquidity + ROA + 
                                        TotalLoans_TotalAssets + Z_score + 
                                        gos_sobstv + foreign + system + A_Shares +
                                        A_bonds + A_capitals + A_loro_loans + A_fixed_assets +
                                        P_deposits_individuals + P_corporate_funds + P_capitals,
                          data = data,
                          marginal = list(hpa = 3))

summary(model_orsemi)

c(probit = AIC(model_orprobit), logit = AIC(model_orlogit), semiparametric = AIC(model_orsemi))
c(probit = BIC(model_orprobit), logit = BIC(model_orlogit), semiparametric = BIC(model_orsemi))
c(probit = logLik(model_orprobit), logit = logLik(model_orlogit), semiparametric = logLik(model_orsemi))

#---------------------------------------------------
# Часть 3. Проверка гипотез
#---------------------------------------------------

# Проверим гипотезу о том, что porfolio_cluster_1 оказывает такое же влияние на 
# индекс стабильности как и porfolio_cluster_2

fn_test = function(object)
{
  coef_val = coef(object, eq = 1)
  val = coef_val["porfolio_cluster_1"] - coef_val["porfolio_cluster_2"]
  return(val)
}

test.1 <- delta_method(model_orprobit, fn = fn_test)
summary(test.1)

test.1 <- delta_method(model_orlogit, fn = fn_test)
summary(test.1)

test.1 <- delta_method(model_orsemi, fn = fn_test)
summary(test.1)

#---------------------------------------------------
# Часть 4. Предельные эффекты и их значисость
#---------------------------------------------------

# Посчитаем средний предельный эффект перемнной
# в сравнение с базовым на вероятность попасть в 
# ту или иную группу

# По критериям информативности будем использовать логит модель 

# porfolio_cluster
data.porfolio_cluster = data
data.porfolio_cluster$porfolio_cluster_1 = 0
data.porfolio_cluster$porfolio_cluster_2 = 0
data.porfolio_cluster$porfolio_cluster_3 = 0
data.porfolio_cluster$porfolio_cluster_4 = 0

ame.p1_g0 <- mean(predict(model_orlogit, group = 0, type = "prob", 
                             me = "porfolio_cluster_1", eps = c(0, 1),
                             newdata = data.porfolio_cluster))

ame.p1_g1 <- mean(predict(model_orlogit, group = 1, type = "prob", 
                                 me = "porfolio_cluster_1", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p1_g2 <- mean(predict(model_orlogit, group = 2, type = "prob", 
                                 me = "porfolio_cluster_1", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p1_g3 <- mean(predict(model_orlogit, group = 3, type = "prob", 
                                 me = "porfolio_cluster_1", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p1_g4 <- mean(predict(model_orlogit, group = 4, type = "prob", 
                                 me = "porfolio_cluster_1", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p2_g0 <- mean(predict(model_orlogit, group = 0, type = "prob", 
                                 me = "porfolio_cluster_2", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p2_g1 <- mean(predict(model_orlogit, group = 1, type = "prob", 
                                 me = "porfolio_cluster_2", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p2_g2 <- mean(predict(model_orlogit, group = 2, type = "prob", 
                                 me = "porfolio_cluster_2", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p2_g3 <- mean(predict(model_orlogit, group = 3, type = "prob", 
                                 me = "porfolio_cluster_2", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

ame.p2_g4 <- mean(predict(model_orlogit, group = 4, type = "prob", 
                                 me = "porfolio_cluster_2", eps = c(0, 1),
                                 newdata = data.porfolio_cluster))

# fin_cluster          
data.fin_cluster = data
data.fin_cluster$fin_cluster_1 = 0
data.fin_cluster$fin_cluster_2 = 0
data.fin_cluster$fin_cluster_3 = 0
data.fin_cluster$fin_cluster_4 = 0
data.fin_cluster$fin_cluster_5 = 0

ame.f4_g0 <- mean(predict(model_orlogit, group = 0, type = "prob", 
                                 me = "fin_cluster_4", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f4_g1 <- mean(predict(model_orlogit, group = 1, type = "prob", 
                                 me = "fin_cluster_4", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f4_g2 <- mean(predict(model_orlogit, group = 2, type = "prob", 
                                 me = "fin_cluster_4", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f4_g3 <- mean(predict(model_orlogit, group = 3, type = "prob", 
                                 me = "fin_cluster_4", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f4_g4 <- mean(predict(model_orlogit, group = 4, type = "prob", 
                                 me = "fin_cluster_4", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f5_g0 <- mean(predict(model_orlogit, group = 0, type = "prob", 
                                 me = "fin_cluster_5", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f5_g1 <- mean(predict(model_orlogit, group = 1, type = "prob", 
                                 me = "fin_cluster_5", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f5_g2 <- mean(predict(model_orlogit, group = 2, type = "prob", 
                                 me = "fin_cluster_5", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f5_g3 <- mean(predict(model_orlogit, group = 3, type = "prob", 
                                 me = "fin_cluster_5", eps = c(0, 1),
                                 newdata = data.fin_cluster))

ame.f5_g4 <- mean(predict(model_orlogit, group = 4, type = "prob", 
                                 me = "fin_cluster_5", eps = c(0, 1),
                                 newdata = data.fin_cluster))

# test me clusters

me.cl.fn <- function(object, group, me)
{
  val <- mean(predict(object, group = group, type = "prob", 
                      me = me, eps = c(0, 1),
                      newdata = data.fin_cluster))
  return(val)
}

me.cl.test.p1_g0 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(0, "porfolio_cluster_1"))
summary(me.cl.test.p1_g0)

me.cl.test.p1_g1 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(1, "porfolio_cluster_1"))
summary(me.cl.test.p1_g1)

me.cl.test.p1_g2 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(2, "porfolio_cluster_1"))
summary(me.cl.test.p1_g2)

me.cl.test.p1_g3 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(3, "porfolio_cluster_1"))
summary(me.cl.test.p1_g3)

me.cl.test.p1_g4 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(4, "porfolio_cluster_1"))
summary(me.cl.test.p1_g4)

me.cl.test.p2_g0 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(0, "porfolio_cluster_2"))
summary(me.cl.test.p2_g0)

me.cl.test.p2_g1 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(1, "porfolio_cluster_2"))
summary(me.cl.test.p2_g1)

me.cl.test.p2_g2 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(2, "porfolio_cluster_2"))
summary(me.cl.test.p2_g2)

me.cl.test.p2_g3 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(3, "porfolio_cluster_2"))
summary(me.cl.test.p2_g3)

me.cl.test.p2_g4 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(4, "porfolio_cluster_2"))
summary(me.cl.test.p2_g4)

me.cl.fn <- function(object, group, me)
{
  val <- mean(predict(object, group = group, type = "prob", 
                      me = me, eps = c(0, 1),
                      newdata = data.porfolio_cluster))
  return(val)
}

me.cl.test.f4_g0 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(0, "fin_cluster_4"))
summary(me.cl.test.f4_g0)

me.cl.test.f4_g1 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(1, "fin_cluster_4"))
summary(me.cl.test.f4_g1)

me.cl.test.f4_g2 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(2, "fin_cluster_4"))
summary(me.cl.test.f4_g2)

me.cl.test.f4_g3 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(3, "fin_cluster_4"))
summary(me.cl.test.f4_g3)

me.cl.test.f4_g4 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(4, "fin_cluster_4"))
summary(me.cl.test.f4_g4)

me.cl.test.f5_g0 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(0, "fin_cluster_5"))
summary(me.cl.test.f5_g0)

me.cl.test.f5_g1 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(1, "fin_cluster_5"))
summary(me.cl.test.f5_g1)

me.cl.test.f5_g2 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(2, "fin_cluster_5"))
summary(me.cl.test.f5_g2)

me.cl.test.f5_g3 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(3, "fin_cluster_5"))
summary(me.cl.test.f5_g3)

me.cl.test.f5_g4 <- delta_method(model_orlogit, fn = me.cl.fn, fn_args =list(4, "fin_cluster_5"))
summary(me.cl.test.f5_g4)

# securities 
ame.sec_g0 <- mean(predict(model_orlogit, group = 0, type = "prob", me = "securities"))
ame.sec_g1 <- mean(predict(model_orlogit, group = 1, type = "prob", me = "securities"))
ame.sec_g2 <- mean(predict(model_orlogit, group = 2, type = "prob", me = "securities"))
ame.sec_g3 <- mean(predict(model_orlogit, group = 3, type = "prob", me = "securities"))
ame.sec_g4 <- mean(predict(model_orlogit, group = 4, type = "prob", me = "securities"))

me.sec.fn <- function(object, group)
{
  val <- mean(predict(object, group = group, type = "prob", me = 'securities'))
  return(val)
}

me.sec.test.g0 <- delta_method(model_orlogit, fn = me.sec.fn, fn_args =list(0))
summary(me.sec.test.g0)

me.sec.test.g1 <- delta_method(model_orlogit, fn = me.sec.fn, fn_args =list(1))
summary(me.sec.test.g1)

me.sec.test.g2 <- delta_method(model_orlogit, fn = me.sec.fn, fn_args =list(2))
summary(me.sec.test.g2)

me.sec.test.g3 <- delta_method(model_orlogit, fn = me.sec.fn, fn_args =list(3))
summary(me.sec.test.g3)

me.sec.test.g4 <- delta_method(model_orlogit, fn = me.sec.fn, fn_args =list(4))
summary(me.sec.test.g4)

