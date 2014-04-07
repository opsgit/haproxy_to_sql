

Sometimes you just have to make it work and not worry about technical/architectural debt.

This simple set of scripts is a product of that. We spent a ton of time trying to figure a
great logging architecture and it never seemed to go anywhere. So, eschewing scope creep and 
every other enemy of getting shit done, I wrote a quick python script that tails/parses haproxy logs
and pushes to mysql to that a frontend can consume/display it prettily.

Of all other approaches we kinda tried, this was the simplest to get from start to deployed and 
the value is obvious.

Here's to solving the problem and moving on!

