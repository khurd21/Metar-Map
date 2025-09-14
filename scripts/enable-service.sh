#!/usr/bin/env bash

sudo systemctl daemon-reload
sudo systemctl enable metar-map
sudo systemctl start metar-map