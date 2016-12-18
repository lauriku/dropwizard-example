# vim: syntax=groovy

def mavenImage = docker.image("maven:3.3.9-jdk-8")

mavenImage.pull()

stage("Package") {
  mavenImage.inside {
    git url: "https://github.com/lauriku/dropwizard-example.git"
    sh "mvn package"
   }
}
