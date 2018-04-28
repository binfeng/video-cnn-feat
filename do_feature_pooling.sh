overwrite=0
rootpath=$HOME/VisualSearch
feature=pyresnet-152_imagenet11k,flatten0_output,os
pooling=mean

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 collection [rootpath]"
    exit
fi

collection=$1

if [ "$#" -gt 1 ]; then
    rootpath=$2
fi

python -m videocnn.feature_pooling $collection \
    --overwrite $overwrite \
    --rootpath $rootpath \
    --feature $feature \
    --pooling $pooling