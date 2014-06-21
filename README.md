smarthome-deployment
====================

Deployment scripts for SmartHome services.

# Usage

Install *ansbile*: `[sudo] pip install ansible` and check that `ansible-playbook` got added to your `$PATH`. (Tested with version 1.5.3.)

Then put a ssh keyfile with read access to the GitHub repositories at the path `keys/smarthome-services{.pub}` (it will also be the admin user ssh key).

And one with write access to the remote data endpoint at the path `keys/smarthome-remote-key`.

NOTE: these playbooks have been tested with passwordless keyfile access to both GitHub and EC2. They might get stuck with password prompts. Consider using `ssh-agent`.

## EC2 setup

First you will need to get a **ACCESS_KEY** and a **SECRET_KEY** for your account and set them as environment variables.

Ansible is a bit quirky and requires two different names for each values.

My suggestion is to create a `~/.aws/env.sh` file like this

```
export AWS_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXX
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_KEY=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
export AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
export EC2_REGION=us-east-1
```

and import it with `. ~/.aws/env.sh`.

Then, you will need to `[sudo] pip install boto`.

Finally, to update instances you will need the EC2 inventory plugin.

Download it as follows

```
wget https://raw.github.com/ansible/ansible/devel/plugins/inventory/ec2.ini
wget https://raw.github.com/ansible/ansible/devel/plugins/inventory/ec2.py
chmod +x ec2.py
```

## Type: Drivers hub

### EC2

#### New instance

To launch a new instance first create an appropriate keypair and security group (just allow SSH) from the AWS Console.

Then, launch a new instance with

```
ansible-playbook -i inventory.ini ec2.yml --extra-vars "operation=new keypair_name=KEYPAIR security_group=GROUP"
```

This will create a new *t1.micro* instance in *us-east-1*, fully configured.

You can login as the user `admin` with the keypair you specified.

#### Updating all the hub instances

Simply run

```
ansible-playbook -i ec2.py ec2.yml --extra-vars "operation=update"
```

This will get all the tagged hub instances in your account to the current version of the playbook.

### RPi

System requirements:

* installed Raspbian
* [recommended] expanded root partition

Add the RPi IP(s) to `inventory.ini` like this

```
[raspberrypi]
192.168.1.43
```

For the first deploy you will need *sshpass* for not typing in the default password interactively. OS X users can install it with

```
brew install https://gist.githubusercontent.com/stefanoverna/1513663/raw/3e98bf9e03feb7e31eeddcd08f89ca86163a376d/sshpass.rb
```

Then use this command for the first deploy

```
sshpass -p raspberry ansible-playbook -k -i inventory.ini rpi.yml
```

After the first deploy, you can update with simply

```
ansible-playbook -i inventory.ini rpi.yml
```

### Custom hub_id

You can specify the hub id and classes by adding the following argument to any call of `ansible-playbook`

```
--extra-vars="user_hub_id=aa71379e-c92c-4891-8453-0003b1f9d9ef hub_classes=demo"
```

Required format is `[a-z0-9-]+`.

### Repository overrides

It's possible to override the version of the repositories deployed.

Simply copy the overrides you want from `repo_overrides.yml.example` to `repo_overrides.yml` and invoke `ansible-playbook` with

```
--extra-vars="repo_overrides=repo_overrides.yml"
```

Overrides are persisted for updates.
