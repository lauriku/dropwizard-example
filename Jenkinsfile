def mavenImage = docker.image("maven:3.3.9-jdk-8")

mavenImage.pull()

def mavenOpts = "-Dmaven.repo.local=${env.JENKINS_HOME}/.m2/repository"

stage("Build") {
  mavenImage.inside {
    withEnv(["MAVEN_OPTS=${mavenOpts}"]) {
      sh 'mvn compile'
    }
  }
}
