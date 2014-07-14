diamondhead
===========

Script to determine if the stock market is currently over or underpriced based on historical averages, then text me the fraction of stocks to buy and cash to hold.

We find an exponential curve that fits the S&P 500 from 1950 to present.  Based loosely on waterfilling power in noisy channels for information theory, I use some simple gradient optimization to find the parameters of a model that would have maximized historical return given a fixed monthly budget.

This model determines whether the stock market is expensive or cheap by an optimally shifted exponential fit curve, then chooses to buy $\alpha d + \beta$ fraction stocks and hold $1.0 - \alpha d + \beta$ in cash, where $d$ is the discount.  $\alpha$ and $\beta$ differ for when $d$ is at a premium or at a discount.
