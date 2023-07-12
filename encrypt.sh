#!/bin/bash

ansible-vault encrypt ./.env --vault-password-file key
