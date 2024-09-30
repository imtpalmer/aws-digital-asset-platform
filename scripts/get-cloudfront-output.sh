#!/bin/bash

echo $(cd ../infra;terraform output -raw react_app_url)