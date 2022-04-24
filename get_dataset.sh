
num_days=$1
filename=$2


#In this script we will define the procedure that updates the raw dataset"
echo "We start with downloading the data"
python msix/load_data/multithread.py --ndays $num_days --name $filename     
echo "successfully downloaded your yahoo dataset"
# echo "now we will transform the dataset and save it with TREND features and 5 LAGS"
# python numerai_signals/transformer/transform.py --command trend --lags 5 --ntickers $no_tickers --name $filename
