# Interactive Log Visualizer

This library supports interactive visualization of training logs of neural networks.
More specifically, this targets the scenario where you need to visualize tens and hundreds of experiment results.

This library supports two features.

+ Interactive visualization of logs
+ Some helper functions to prepare train logs so that visualization can start. This part is framework dependent.

# Installation

```
pip install ilv
```


## Dependencies

+ Pandas
+ Bokeh (0.12.4 and higher)


## Examples

### fully working example
On GPU enabled machine, run following commands.
You need to install a deep learning framework Chainer to run this.

```
cd examples/train_mnist/
./run_train.sh  # wait until all experiments finish
bokeh serve --show bokeh_app.py
```
