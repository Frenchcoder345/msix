indicators=$1
lag=$2

echo "now we will transform the dataset and save it with $indicators features and 5 LAGS"

python msix/transformer/transform.py --command $indicators --lags $lag
python msix/transformer/final_formatting.py --indicator $indicators

echo "..............................Completed set 1................................."


# python numerai_signals/transformer/transform.py --command volatility --lags 5 --startticker 501 --endticker 1000 --name '2'
# echo "..............................Completed set 2................................."
# python numerai_signals/transformer/transform.py --command volatility --lags 5 --startticker 1001 --endticker 1500 --name '3'
# echo "..............................Completed set 3................................."

# python numerai_signals/transformer/transform.py --command volatility --lags 5 --startticker 1501 --endticker 2000 --name '4'
# echo "..............................Completed set 4................................."

# python numerai_signals/transformer/transform.py --command volatility --lags 5 --startticker 2001 --endticker 2500 --name '5'
# echo "..............................Completed set 5................................."

# python numerai_signals/transformer/transform.py --command volatility --lags 5 --startticker 2501 --endticker 3000 --name '6'
# echo "..............................Completed set 6................................."
