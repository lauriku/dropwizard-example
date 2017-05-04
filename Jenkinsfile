#!/usr/bin/env groovy
def mavenImage = docker.image("maven:3.3.9-jdk-8")
def packerImage = docker.image("hashicorp/packer:light")
def alpineImage = docker.image("alpine")

def artifactBucket = "gofore-aws-training-artifacts"

def artifact

mavenImage.pull()
packerImage.pull()

def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

stage("Build") {
  mavenImage.inside {
    git url: 'https://github.com/lauriku/dropwizard-example.git'
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
      sh 'mvn package'
    }
    archiveArtifacts artifacts: 'target/dropwizard-*SNAPSHOT.jar', fingerprint: true
    stash name: 'package', includes: 'target/dropwizard-*SNAPSHOT.jar, example.yml, dropwizard-init-script'
  }
}

stage("Upload package to S3") {
  node {
    unstash 'package'
    artifact = "${env.JOB_NAME}-${env.BUILD_NUMBER}.zip"
    sh "zip -rq ${artifact} ."
    sh "aws s3 cp ${artifact} s3://${artifactBucket}/"
  }
}

stage("Build new AMI") {
  packerImage.inside {
    unstash 'compiled'
    sh 'packer build basic.json'
  }
}
