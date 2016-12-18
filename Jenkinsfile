#!/usr/bin/env groovy

def mavenImage = docker.image("maven:3.3.9-jdk-8")
def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

mavenImage.pull()

stage("Compile") {
  mavenImage.inside {
    git url: "https://github.com/lauriku/dropwizard-example.git"
    withEnv(["MAVEN_OPTS=$mavenOpts"]) {
      sh "mvn compile"
    } 
    stash name: 'compiled', includes: '*/**'
  }
}

stage("Test") {
  mavenImage.inside {
    unstash 'compiled'
    withEnv(["MAVEN_OPTS=$mavenOpts"]) {
      sh 'mvn test'
    }
    step([$class: 'JUnitResultArchiver', testResults: '**/target/surefire-reports/*.xml'])
  }
}

stage("Package") {
  mavenImage.inside {
    unstash 'compiled'
    withEnv(["MAVEN_OPTS=$mavenOpts"]) {
      sh 'mvn package'
    }
    archiveArtifacts artifacts: 'target/dropwizard-*SNAPSHOT.jar', fingerprint: true
    stash name: 'jar', includes: 'target/dropwizard-*SNAPSHOT.jar'
  }
}
