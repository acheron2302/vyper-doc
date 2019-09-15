# VYPER-DOC

A python script to turn your docstring inside contract into json userdoc and devdoc like solidity compiler

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
You need argparse python3 version, run this command on your terminal to install it:
```
pip3 install argparse
```

### Installing

To install it just clone it into your folder, run this command:
```
git clone https://github.com/acheron2302/vyper-doc.git ~/opt/vyper-doc
```

Then for your terminal to run it just by typing vyper-doc, you need to run setup.sh with root privilege:
```
sudo ./setup.sh
```
**notice:** The run on terminal is only work with linux and haven't support mac

## Usage example

This script use the [vyper document natspec](https://vyper.readthedocs.io/en/latest/structure-of-a-contract.html#natspec-metadata) to turn your contract into json doc.

#### Example
The example contract:
```
x: uint256


@public
def store(_value: uint256):
  """
    @author acheron2302
    @notice store the value to this contract
    @dev store the value to this contract
    @param _value The value to store in this contract
  """
  x = _value


@public
@constant
def get() -> uint256:
  """
    @author acheron2302
    @notice get back the value store in this contract
    @dev get back the value for 
    this contract
    @return the value that is store in this contract
  """
  return x

```

To get back the user document run this command:
```
$ vyper-doc --userdoc file_path
```
The result on the above contract:
```
{
    "methods": {
        "store(uint256)": {
            "notice": "store the value to this contract"
        }
    }
}

```
And to get back the dev doc run this command:
```
$ vyper-doc --devdoc file_path
```

The result on the above contract:
```
{
    "methods": {
        "store(uint256)": {
            "author": "acheron2302",
            "dev": "store the value to this contract"
        }
    }
}


```

#### Notice
You **MUST** follow this rule for the script to work:
* **YOU MUST RUN THIS SCRIPT WITH VYPER COMPILER ALREADY OPEN AND RUN ON YOUR TERMINAL**. If you haven't install vyper compiler then you can follow [this instruction on their document](https://vyper.readthedocs.io/en/latest/installing-vyper.html)
* This script only work if you **write the natspec inside the function**
* You can only have 1 dev, 1 notice and 1 author in each function. But if you need more than 1 then you can write in multiple line like in the example
* The setup.sh is only support linux for now
* The reason the return function did not work is because my regex fucked up (gonna fix it)

## Contact
email: acheron2302@protonmail.com
