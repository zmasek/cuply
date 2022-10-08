Workflow:
=========

The Arduino library is from: https://github.com/vascop/Python-Arduino-Proto-API-v2 and it's heavily modified so it's included in the `backend.arduino` folder.

When the Arduino is attached to the USB, run this if you don't run docker with `sudo`::

    sudo chmod 777 /dev/ttyACM0

Have docker-compose installed beforehand (sudo apt install docker-compose). Go in the repo folder and execute docker::

    sudo docker-compose up -d

Provided `Makefile` handles some of the things so if you want to execute back-end tests, run `make test`.

There's a leftover I need to solve and it involves running front-end separately. That's why `nodeenv` package is in the requirements and it handles node 16.16.0 on my old setup. Some kind of virtualization is required for running front-end and it can be run during testing on a separate machine with the `setupProxy.js` handling the connections. In my case, during testing, I had Raspberry with Arduino in the local network running as the back-end with docker, then on the other machine in the same network I had front-end. I did::

    python -m venv venv
    pip install -r backend/requirements.txt
    source venv/bin/activate
    nodeenv --node=16.16.0 --prebuilt -p
    # sanity check
    deactivate
    source venv/bin/activate
    source profile # mentioned below because profile is not in the repo
    # then in the frontend folder where it would use package.json
    npm install
    npm start run

Without docker for the front-end, there's a `profile` file and `source profile` is run. `.env.template` gives you a list of variables needed. Mainly react ones are required for the `setupProxy.js` to work. Honcho was executing things, but it's avoided with docker. Some leftovers are still present, though.


Sketch:
=======

You would need to use `arduino-cli` to compile the sketch unless you are installing it through the IDE. Run once and forget unless you need to access Arduino board again. Official video instructions exist: https://www.youtube.com/watch?v=J-qGn1eEidA

A series of commands to do it without IDE::

    cd sketch
    arduino-cli compile -b arduino:sam:arduino_due_x_dbg
    arduino-cli upload -b arduino:sam:arduino_due_x_dbg -p /dev/ttyACM0

TODO:
=====

1. Fix front-end container workflow
2. SECURITY, SECURITY, SECURITY. Updating packages and having sensitive information outside of the repo.
3. "Add new card" functionality
4. "Remove existing card"
5. Bring back dashboard layout (rearrange cards)
