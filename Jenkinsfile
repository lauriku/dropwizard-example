#!/usr/bin/env groovy
def mavenImage = docker.image("maven:3.3.9-jdk-8")
def alpineImage = docker.image("alpine")

def artifactBucket = "gofore-aws-training-artifacts"

def artifact
def amiId

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
    sh "zip -rq ${artifact} target/dropwizard-*SNAPSHOT.jar example.yml dropwizard-init-script"
    sh "aws s3 cp --acl public-read ${artifact} s3://${artifactBucket}/"
  }
}

stage("Build new AMI") {
  node {
    unstash 'compiled'
    artifact = "${env.JOB_NAME}-${env.BUILD_NUMBER}.zip"
    withEnv(["ARTIFACT=${artifact}", "BUCKET=${artifactBucket}"]) {
      sh 'packer build -color=false basic.json | tee build.log'
      amiId = sh(returnOutput: true, script: "grep 'artifact,0,id' build.log | cut -d, -f6 | cut -d: -f2")   
    }
  }
}

stage("Create new launch config") {
  node {
    sh "echo ${amiId}"
  }
}
