#!/usr/bin/env groovy

def mavenImage = docker.image("maven:3.3.9-jdk-8")
def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

mavenImage.pull()

stage("Package") {
  mavenImage.inside {
    git url: "https://github.com/lauriku/dropwizard-example.git"
    withEnv(["MAVEN_OPTS=$mavenOpts"]) {
      sh "mvn package"
    } 
    }
}
