### Explanation

When we train Machine Learning models like linear regressions, logistic
regressions, or neural networks, we do so by defining a loss function
and minimizing that loss function. A loss function is a metric for
measuring how your model is performing where lower is better. For
example, Mean Squared Error is a loss function that measures the squared
distance (on average) between a model's guesses and the true values.

$$MSE = \\frac{1}{n} \\sum_{i=1}^{n} (Y_i - \hat{Y}_i)^2$$

Regularization works by adding a penalty to the loss function in order
to penalize large model parameters. In Linear Regression, the penalty
increases when the size of the coefficients increases. Because the loss
function is made up of two things: the original loss function (the MSE,
here) and the penalty, predictors must 'pull their weight' by reducing
the MSE enough to be 'worth' the penalty. This causes small, unimportant
predictors to have small or zero coefficients.

LASSO (L1) and Ridge (L2) are two common forms of Regularization. LASSO
adds a penalty to the loss function by taking the absolute value of each
parameter/coefficient, and adding them all together. Ridge adds a
penalty to the loss function by taking the square of each
parameter/coefficient, and adding them all together.

\$$LASSO = \\frac{1}{n} \\sum_{i=1}^{n} (Y_i - \hat{Y}\_i)^2 + \\lambda \\underbrace{\\sum\_{j=1}^{p} |\\beta_j|}_\\text{penalty}$$

$$Ridge = \\frac{1}{n} \\sum_{i=1}^{n} (Y_i - \hat{Y}\_i)^2 + \\lambda \\underbrace{\\sum\_{j=1}^{p} \\beta_j^2}_\\text{penalty}$$

When using regularization, we must choose the regularization strength
(see slider above) which is a number that scales how harshly we
penalize. If we multiply the penalty by 0, that's the same as not having
a penalty at all. But if we multiply the penalty by 500, that would
penalize the parameters a lot more.

$$\\lambda \\text{is the regularization strength.}$$

### Explore

##### Comparing LASSO, Ridge, and Linear Regression

With the slider at 0.1 (the default) look at the boxplot at the top of
the page. This shows the coefficients from 1000 simulated data sets. For
each data set the 'vowels' (A, E, I, O, U, Y, W) do have some
relationship with the outcome (X) that our model is predicting. A has
the largest effect then E, I, O, U, Y and finally W has the smallest
effect on X. The Consonants (B,C,D,G,H,J,K) have absolutely no effect on X.

Look at the Graph and ask yourself these questions:

-   Which model (Linear, LASSO, Ridge) tends to have the highest
    coefficients? What does this tell you about the various penalties
    each model has?
-   What happens to the LASSO coefficients for the Consonant predictors
    (B-K) which have no real effect on X?
-  The Linear and Ridge Coefficients look similar for the Consonants
    (B-K) but what's slightly different between them? What does that
    tell you about what Ridge penalties do?
-   Are the larger effects (A-I) affected differently than the smaller
    effects (O-W) when you increase the Regularization Strength?

##### Comparing Different Regularization Strengths

Now, using the slider at the top of the page, change the Regularization
Strength. Try values that are very low, moderate, and very high.

Look at the Graph and ask yourself these questions:

-   What happens to the LASSO and Ridge models when the Regularization 
    Strength is almost 0?
-   What happens to the LASSO model's coefficients when the
    Regularization Strength is very high?
-   Do the Linear Regression coefficients change when you change
    Regularization Strength? (if so, why, if not, why not?)