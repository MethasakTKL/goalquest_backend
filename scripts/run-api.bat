#!/bin/bash

uvicorn "goalquest_backend.main:create_app" --factory --reload