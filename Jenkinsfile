#!/usr/bin/env groovy
def mavenImage = docker.image("maven:3.3.9-jdk-8")
def alpineImage = docker.image("alpine")

def artifactBucket = "gofore-aws-training-artifacts"

def artifact

mavenImage.pull()

def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

stage("Clone Repo") {
  mavenImage.inside {
    git url: 'https://github.com/lauriku/dropwizard-example.git', branch: 'aws-training'
  }
  stash name: 'source', includes: '*'
}

stage("Build") {
  mavenImage.inside {
    unstash 'source'
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn compile'
    }
  }
}

stage("Test") {
  mavenImage.inside {
    unstash 'source'
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn test'
    }
    step([$class: 'JUnitResultArchiver', testResults: 'target/surefire-reports/*.xml'])
  }
}

stage("Package") {
  mavenImage.inside {
    unstash 'source'
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
    sh "zip -rq ${artifact} ."
    sh "aws s3 cp ${artifact} s3://${artifactBucket}/"
  }
}

stage("Build new AMI") {
  node {
    unstash 'compiled'
    withEnv(["ARTIFACT=${artifact}", "BUCKET=${artifactBucket}"]) {
      sh 'packer build -color=false basic.json'
    }
  }
}
