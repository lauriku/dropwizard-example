#!/usr/bin/env groovy
def mavenImage = docker.image("maven:3.3.9-jdk-8")
def alpineImage = docker.image("alpine")

def artifactBucket = "gofore-aws-training-artifacts"
def autoScalingGroupName = "dropwizard-example-asg"

def artifact

mavenImage.pull()

def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

stage("Build") {
  mavenImage.inside {
    git url: 'https://github.com/lauriku/dropwizard-example.git', branch: 'aws-training'
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn compile'
    }
    stash name: 'compiled', includes: '*/**'
  }
}

stage("Test") {
  mavenImage.inside {
    unstash 'compiled'
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn test'
    }
    step([$class: 'JUnitResultArchiver', testResults: 'target/surefire-reports/*.xml'])
  }
}

stage("Package") {
  mavenImage.inside {
    unstash 'compiled'
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn -Dmaven.test.skip=true package'
    }
    archiveArtifacts artifacts: 'target/dropwizard-*SNAPSHOT.jar', fingerprint: true
    stash name: 'package', includes: 'target/dropwizard-*SNAPSHOT.jar, example.yml, dropwizard-init-script'
  }
}

stage("Upload package to S3") {
  node {
    unstash 'package'
    artifact = "${env.JOB_NAME}-${env.BUILD_NUMBER}.zip"
    sh "zip -rq ${artifact} target/dropwizard-*SNAPSHOT.jar example.yml dropwizard-init-script example.keystore"
    sh "aws s3 cp --acl public-read ${artifact} s3://${artifactBucket}/"
  }
}

stage("Build new AMI") {
  node {
    unstash 'compiled'
    artifact = "${env.JOB_NAME}-${env.BUILD_NUMBER}.zip"
    withEnv(["ARTIFACT=${artifact}", "BUCKET=${artifactBucket}"]) {
      sh 'packer build -machine-readable basic.json | tee build.log'
    }
    sh("grep 'artifact,0,id' build.log | cut -d, -f6 | cut -d: -f2 > ami_id.txt") 
    stash name: 'deploy', includes: 'ami_id.txt, lc_template.json'
  }
}

stage("Create new launch config") {
  node {
    unstash 'deploy'
    sh "aws autoscaling create-launch-configuration --cli-input-json file://lc_template.json --launch-configuration-name ${env.JOB_NAME}-${env.BUILD_NUMBER} --image-id `cat ami_id.txt`"
  }
}

stage("Update Autoscaling group to use the new config") {
  node {
    sh "aws autoscaling update-auto-scaling-group --auto-scaling-group-name ${autoScalingGroupName} --launch-configuration ${env.JOB_NAME}-${env.BUILD_NUMBER}"
  }
}

stage("Increase autoscaling group instances from 1 to 2") {
  node {
    sh "aws autoscaling update-auto-scaling-group --auto-scaling-group-name ${autoScalingGroupName} --desired-capacity 2"
  }
}
